FROM python:3.6
RUN pip install prometheus_client requests
RUN mkdir -p /opt/spot-instance-exporter
COPY ./Dockerfile /opt/spot-instance-exporter/
COPY ./README.md /opt/spot-instance-exporter/
COPY ./spotinstance.py /opt/spot-instance-exporter/
WORKDIR /opt/spot-instance-exporter

ENTRYPOINT ["python3", "spotinstance.py"]
