
# Zitified Flask API for Detecting Offensive Language

This is a simple Python program the leverages OpenZiti to privately share a Flask API and Transformers library to load
an offensive text classifier model.

## Run the Flask API Server

```bash
#                               <path to Ziti Identity>                             <Ziti Service name>
python ./ziti-classifier-api.py /opt/openziti/etc/identities/classifier-server.json classifier-service
```

## Send an HTTP Request

```bash
curl \
  classifier.private:5000/api/v1/classify \
  --request POST \
  --header 'content-type: application/json' \
  --data '{"text": "I am a little teapot."}';
```

```json
[{"label":"Non-Offensive","score":0.8720483183860779}]
```

## Text Classification Model

Make sure you have the git-lfs executable on your path (https://git-lfs.com) before running the following command.

```bash
git lfs install
```

Download the model from HuggingFace and place it in the `./models` sub-directory in a path that matches the
Python program's loader statement.

```bash
git clone https://huggingface.co/elozano/tweet_offensive_eval ./models/elozano_tweet_offensive_eval
```

## Install Python Dependencies

```bash
pip install -r ./requirements.txt
```

## GPU Acceleration

A GPU is not required to use this example. To enabled GPU acceleration, uncomment `device: 0` to elect the first GPU.  

## OpenZiti Resources

You need a Ziti Identity and Ziti Service for the Flask server to use. Here's an example that creates an Identity for the client and server. With this config your HTTP client should send POST requests to `http://classifier.private:80/api/v1/classify` with a JSON body containing a `text` attribute.

```bash
ziti edge create config "classifier-intercept-config" intercept.v1 \
    '{"protocols":["tcp"],"addresses":["classifier.private"], "portRanges":[{"low":80, "high":80}]}'

ziti edge create service "classifier-service" \
    --configs classifier-intercept-config

ziti edge create service-policy "classifier-bind-policy" Bind \
    --service-roles '@classifier-service' --identity-roles '#classifier-hosts'

ziti edge create service-policy "classifier-dial-policy" Dial \
    --service-roles '@classifier-service' --identity-roles '#classifier-clients'

ziti edge create identity classifier-client --role-attributes classifier-clients

ziti edge create identity classifier-server --role-attributes classifier-hosts
```
