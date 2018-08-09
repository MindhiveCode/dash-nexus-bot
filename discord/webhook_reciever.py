from flask import Flask, request
import os
import json

from pprint import pprint

app = Flask(__name__)


@app.route('/', methods=['POST'])
def foo():
    data = json.loads(request.data)

    print(data)
    pprint(data)

    return "OK"


if __name__ == '__main__':
    port_config = int(os.getenv('PORT', 5000))
    print("Starting up server.")

    if os.environ.get('ENVIRONMENT') == 'PRODUCTION':
        print("Running in PRODUCTION environment")
    else:
        print("Running in DEVELOPMENT environment")

    if os.name == 'nt':
        app.run(host='127.0.0.1', port=port_config, debug=True)
    else:
        app.run(host='0.0.0.0', port=port_config, debug=False)

