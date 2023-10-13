
# Zitified Flask API for Detecting Offensive Language

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

A GPU is not required to use this example. To enabled GPU acceleration, uncomment `device: 0` to elect the first GPU.  
