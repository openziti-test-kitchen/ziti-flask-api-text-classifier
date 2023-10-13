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

classifier = pipeline(
    # device=0,
    task="sentiment-analysis",
    model="elozano/tweet_offensive_eval"
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
    ':8000': bind_opts,
})
def runApp():
    from waitress import serve
    serve(app,port=8000)

@app.route('/')
def greet():  # put application's code here
    app.logger.info('sending greeting response to GET /')
    return 'Post {"text": "input to classify"} to /api/v1/classify'

@app.route('/api/v1/classify', methods=['POST'])
def classify():
    input = request.json['text']
    result = classifier(input)[0]
    app.logger.info('input: %s, label: %s, score: %s', repr(input), result['label'], result['score'])
    return result


if __name__ == '__main__':
    bind_opts['ztx'] = sys.argv[1]
    bind_opts['service'] = sys.argv[2]
    runApp()
