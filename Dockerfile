
# PyTorch supports <= 3.7.9
FROM python:3.7.9

# provide a named volume here to accelerate startup, writeable by "nobody" too if you want the app to be able to update
# the cache, e.g. ❯ docker run --user root --entrypoint='' --rm --volume models:/app/models busybox chown -Rc 65534:65534 /app/models
ENV TRANSFORMERS_CACHE=/app/models
ENV ZITI_LOG=3

RUN mkdir -p /app \
    && chown -R 65534:65534 /app

COPY ./ziti-classifier-api.py ./requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --requirement /app/requirements.txt \
    && rm -rf /root/.cache/pip

WORKDIR /app
USER nobody

# requires two positional params: Ziti identity JSON file to load context from, and the Ziti service name to host, e.g.:
# python ./ziti-classifier-api.py /opt/openziti/etc/identities/oobabooga-server.json classifier-service
ENTRYPOINT [ "python", "/app/ziti-classifier-api.py" ]