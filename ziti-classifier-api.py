#  Copyright (c)  NetFoundry Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from flask import Flask, request
import openziti
import sys
from transformers import pipeline
from logging.config import dictConfig

SENTIMENTS = {
    'positive': "Not Offensive",
    'neutral': "Not Offensive",
    'negative': "Offensive",
}
LABELS = {
    'positive': SENTIMENTS['positive'],
    'neutral': SENTIMENTS['neutral'],
    'negative': SENTIMENTS['negative'],
    'LABEL_0': SENTIMENTS['positive'],
    'LABEL_1': SENTIMENTS['negative'],
    'non-toxic': SENTIMENTS['positive'],
    'toxic': SENTIMENTS['negative'],
    'SFW': SENTIMENTS['positive'],
    'NSFW': SENTIMENTS['negative'],
    "nothate": SENTIMENTS['positive'],
    "hate": SENTIMENTS['negative'],
}

classifier = pipeline(
    # device=0,
    task="text-classification",
    # model="michellejieli/NSFW_text_classifier",   # most sensitive
    model="facebook/roberta-hate-speech-dynabench-r4-target",
    # model="s-nlp/roberta_toxicity_classifier",  # least sensitive
    top_k=1,  # return the predicted sentiment only so we don't need to sort by score
)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
bind_opts = {}  # populated in main

# the port number must match the waitress serve() port
@openziti.zitify(bindings={
    ':5000': bind_opts,
})
def runApp():
    from waitress import serve
    serve(app,port=5000)

def runAppNoZiti():
    from waitress import serve
    serve(app,port=5000)

@app.route('/')
def greet():  # put application's code here
    app.logger.info('sending greeting response to GET /')
    return 'Post {"text": "input to classify"} to /api/v1/classify'

@app.route('/api/v1/classify', methods=['POST'])
def classify():
    input = request.json['text']
    prediction = classifier(input)[0][0]
    sentiment = LABELS[prediction['label']]
    response = [{
        'label': sentiment,
        'score': prediction['score'],
    }]
    app.logger.info('input: %s, label: %s, score: %s', repr(input), sentiment, prediction['score'])
    return response


if __name__ == '__main__':
    if sys.argv[1] == 'noziti':
        runAppNoZiti()
    else:
        bind_opts['ztx'] = sys.argv[1]
        bind_opts['service'] = sys.argv[2]
        runApp()
