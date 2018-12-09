import os
import sys

sys.path.append(os.path.split(__file__)[0])

import logging
from urllib.parse import urlparse

from bernhard import Client
from flask import Flask, request, redirect, make_response, json
from riemann_wrapper import riemann_wrapper

import config
from shortener import UrlShortener

app = Flask(__name__)

shorterer = UrlShortener()
logger = logging.getLogger()

logger.info("starting up")
try:
    riemann_client = Client(host=config.RIEMANN_HOST,
                            port=config.RIEMANN_PORT)
    riemann_client.send({'metric': 1,
                         'service': 'url-shortener.startup',
                         'ttl': 3600})
except:
    riemann_client = None

wrap_riemann = riemann_wrapper(client=riemann_client, prefix='url-shortener.')


@app.route('/404')
@wrap_riemann('missing', tags=['http_404'])
def missing():
    response = make_response(json.dumps({
        "error": "not found"
    }))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/400')
@wrap_riemann('invalid', tags=['http_400'])
def invalid():
    response = make_response(json.dumps({
        "error": "invalid"
    }))
    response.headers['Content-Type'] = 'application/json'
    return response


## short url lookup
@app.route('/<code>')
@wrap_riemann('lookup')
def lookup(code):
    url = shorterer.lookup(code)
    if not url:
        return redirect('/404')
    else:
        return redirect(url)


@app.route('/g/<code>')
@wrap_riemann('lookup_json')
def lookup_json(code):
    url = shorterer.lookup(code)
    if not url:
        return redirect('/404')
    else:
        response = make_response(json.dumps({
            "url": url
        }))
        response.headers['Content-Type'] = 'application/json'
        return response


## short url generation
@app.route('/', methods=['POST'])
@wrap_riemann('creation')
def shorten_url():
    if request.json and 'url' in request.json:
        u = urlparse(request.json['url'])
        if u.netloc == '':
            url = 'http://' + request.json['url']
        else:
            url = request.json['url']
        res = shorterer.shorten(url)
        logger.debug("shortened %s to %s" % (url, res))
        response = make_response(json.dumps(res))
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        logger.info("invalid shorten request")
        return redirect('/400')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=666)
