
# PyTorch supports <= 3.7.9
FROM python:3.6

COPY ./ziti-classifier-api.py ./requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --requirement /app/requirements.txt \
    && rm -rf /root/.cache/pip

# requires two positional params: Ziti identity JSON file to load context from, and the Ziti service name to host, e.g.:
# python ./ziti-classifier-api.py /opt/openziti/etc/identities/oobabooga-server.json classifier-service
ENTRYPOINT [ "python", "/app/ziti-classifier-api.py" ]