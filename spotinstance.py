from prometheus_client import start_http_server, Metric, REGISTRY
import argparse
import json
import logging
import requests
import sys
import time

# logging setup
log = logging.getLogger('spotinstance')
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class SpotMetric():
  def __init__(self):
    self.endpoint = 'http://spot-price.s3.amazonaws.com/spot.js'

  def collect(self):
    # query the api
    r = requests.get(self.endpoint)
    request_time = r.elapsed.total_seconds()
    log.info('elapsed time -' + str(request_time))
    response = json.loads(r.text[ r.text.index("(") + 1 : r.text.rindex (")") ])
    metric = Metric('spotinstance_api_response_time', 'Total time for the AWS Spot Instance API to respond.', 'summary')
    # add the response time as a metric
    metric.add_sample('spotinstance_api_response_time', value=float(request_time), labels={'name': 'AWS Spot Instance Pricing API'})
    yield metric
    metric = Metric('spotinstance', 'spot instance pricing', 'gauge')
    # each['region'] = us-east
    for each in response['config']['regions']:
      # each['sizes'] = list of instance sizes
      for that in each['instanceTypes']:
        for it in that['sizes']:
          if it['valueColumns'][0]['prices']['USD'] != 'N/A*':
            metric.add_sample('spotinstance', value=float(it['valueColumns'][0]['prices']['USD']), labels={'region': each['region'], 'size': it['size'].replace('.', '_')})
    yield metric

if __name__ == '__main__':
  try:
    parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', nargs='?', const=9101, help='The TCP port to listen on.  Defaults to 9101.', default=9101)
    args = parser.parse_args()
    log.info(args.port)
  
    REGISTRY.register(SpotMetric())
    start_http_server(int(args.port))
    while True:
      time.sleep(60)
  except KeyboardInterrupt:
    print(" Interrupted")
    exit(0)
