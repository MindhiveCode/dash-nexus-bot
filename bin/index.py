from flask import Flask, request
from lib.dc_monkey_patch import *
from flask import jsonify

from pprint import pprint

app = Flask(__name__)


@app.route('/budget', methods=['GET'])
def handle_budget():
    data = get_api_data()
    response = jsonify(data)

    return response


@app.route('/new_proposal', methods=['POST'])
def handle_proposals():
    data = json.loads(request.data)

    print(data)
    pprint(data)

    return "OK"


@app.route('/new_concepet', methods=['POST'])
def handle_concept():
    data = json.loads(request.data)

    print(data)
    pprint(data)

    return "OK"


@app.route('/', methods=['GET'])
def handle_index():
    # data = json.loads(request.data)

    # print(data)
    # pprint(data)

    return "OK"


@app.route('/slack', methods=['POST'])
def handle_slack():
    data = json.loads(request.data)

    print(data)
    pprint(data)

    return "OK"


if __name__ == '__main__':
    port_config = int(os.getenv('PORT', 5000))
    print("Starting up server.")

    if os.environ.get('ENVIRONMENT') == 'PRODUCTION':
        print("Running in PRODUCTION environment")
        app.run(host='0.0.0.0', port=port_config, debug=False)

    else:
        print("Running in DEVELOPMENT environment")

        if os.name == 'nt':
            app.run(host='127.0.0.1', port=port_config, debug=True)
        else:
            try:
                import redis
                redis_url = os.getenv('REDIS_URL', '')
                r = redis.from_url(redis_url)
                r.flushall()
                print("Successfully wiped Redis Cache... CONTINUING")
            except Exception as e:
                print("Failed to wipe Redis Cache ... CONTINUING")
                print(e)

            app.run(host='0.0.0.0', port=port_config, debug=True)

