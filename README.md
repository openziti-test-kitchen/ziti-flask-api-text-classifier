
# Zitified Flask API for Detecting Potentially-Offensive Language

This is a simple Python program the leverages OpenZiti to privately share a Flask API and Transformers library to load
an offensive text classifier model.

## Run the Flask API Server

```bash
#                               <path to Ziti Identity>  <Ziti Service name>
python ./ziti-classifier-api.py ./classifier-server.json classifier-service
```

## Send an HTTP Request

This example assumes an authorized Ziti Identity is loaded in a tunneller running on the same device. The tunneller
provides a nameserver to resolve the Ziti Service address `classifier.private`.

```bash
curl \
  http://classifier.private:80/api/v1/classify \
  --request POST \
  --header 'content-type: application/json' \
  --data '{"text": "I am a little teapot."}';
```

```json
[{"label":"Non-Offensive","score":0.8720483183860779}]
```

This example employs the `zitify` shell script for Linux to run cURL in a Ziti-enabled environment, avoiding the need
for a tunneller running in parallel on the same device. The `zitify` script is available
[from GitHub](https://github.com/openziti/zitify/#readme).

```bash
zitify --identity ./classifier-client.json \
curl \
  http://classifier.private:80/api/v1/classify \
  --request POST \
  --header 'content-type: application/json' \
  --data '{"text": "I am a little teapot."}';
```

## Install Python Dependencies

```bash
pip install -r ./requirements.txt
```

## OpenZiti Resources

The Flask server uses a Ziti Identity and Ziti Service to provide the API to overlay clients. Here's an example that
creates an Identity for the client and server.

```bash
ziti edge create config "classifier-intercept-config" intercept.v1 \
    '{"protocols":["tcp"],"addresses":["classifier.private"], "portRanges":[{"low":80, "high":80}]}'

ziti edge create service "classifier-service" \
    --configs classifier-intercept-config

ziti edge create service-policy "classifier-bind-policy" Bind \
    --service-roles '@classifier-service' --identity-roles '#classifier-hosts'

ziti edge create service-policy "classifier-dial-policy" Dial \
    --service-roles '@classifier-service' --identity-roles '#classifier-clients'

ziti edge create identity classifier-client \
    --role-attributes classifier-clients \
    --jwt-output-file ./classifier-client.jwt

ziti edge create identity classifier-server \
    --role-attributes classifier-hosts \
    --jwt-output-file ./classifier-server.jwt

# produces ./classifier-client.json
ziti edge enroll ./classifier-client.jwt

# produces ./classifier-server.json
ziti edge enroll ./classifier-server.jwt
```

## GPU Acceleration

A GPU is not required to use this example. To disable GPU acceleration, comment `device: 0` to stop electing the first
GPU.

## Docker

Publishing a GitHub release in this repo updates the container image in Docker Hub automatically.

The image is huge.

```bash
$ docker inspect -f "{{ .Size }}" docker.io/openziti/ziti-flask-api-text-classifier:v1 | numfmt --to=si       
4.5G
```

The app runs as `nobody` (uid:gid, 65534:65534), and startup can be accelerated by mounting persistent storage on `/app/models`. That's a writeable cache dir where the large model files are downloaded each time the container starts if not persisted.

```bash
docker run \
  --restart unless-stopped \
  --name classifier-service \
  --volume ./text-classifier-server.json:/app/ziti.json \
  --volume models:/app/models \
  docker.io/openziti/ziti-flask-api-text-classifier:v1 \
    /app/ziti.json \
    classifier-service
```

The last two args are used by the Python program to 1) load Ziti context 2) bind a service by name.

The mounted Ziti identity file needs to be readable by uid 65534.

The optional named volume needs to be writeable by uid 65534. Here's how I prepped the volume before mounting.

```bash
❯ docker volume create models
models

❯ docker run --rm --user root --volume models:/mnt alpine chown -Rc 65534:65534 /mnt
changed ownership of '/mnt' to 65534:65534
```

Now the named volume is ready to mount on the app container.
