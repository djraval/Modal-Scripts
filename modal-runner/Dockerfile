FROM python:3.9

RUN pip install modal

COPY entrypoint.sh /entrypoint.sh
COPY config.ini /config.ini
RUN chmod +x /entrypoint.sh

WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
