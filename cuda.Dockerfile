
# PyTorch supports <= 3.7.9
FROM python:3.7.9 as python

FROM nvidia/cuda:11.1.1-runtime-ubi8

# Copy Python binaries and libraries from the Python image
COPY --from=python /usr/local/bin                      /usr/local/bin
COPY --from=python /usr/local/lib                      /usr/local/lib
COPY --from=python /usr/local/include/python3.7m       /usr/local/include/python3.7m
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN mkdir -p /app \
    && chown -R 65534:65534 /app
COPY ./requirements.txt /app/
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir --requirement /app/requirements.txt \
    && rm -rf /root/.cache/pip

# provide a named volume here to accelerate startup, writeable by "nobody" too if you want the app to be able to update
# the cache, e.g. ❯ docker run --user root --entrypoint='' --rm --volume models:/app/models busybox chown -Rc 65534:65534 /app/models
ENV TRANSFORMERS_CACHE=/app/models
# Ziti C-SDK log level INFO
ENV ZITI_LOG=3
COPY ./ziti-classifier-api.py /app/
WORKDIR /app
USER nobody

# requires two positional params: Ziti identity JSON file to load context from, and the Ziti service name to host, e.g.:
# python ./ziti-classifier-api.py /opt/openziti/etc/identities/oobabooga-server.json classifier-service
ENTRYPOINT [ "python3", "/app/ziti-classifier-api.py" ]