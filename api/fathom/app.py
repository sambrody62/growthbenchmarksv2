# External Imports
from flask import Flask, url_for, jsonify, request
from flask_cors import CORS # pylint: disable=import-error
import firebase_admin # pylint: disable=import-error
from firebase_admin import credentials, auth, firestore # pylint: disable=import-error
import os
import time
import urllib

# Internal Imports
from .config import DevConfig, ProdConfig
from .lib import parse_params, get_benchmarks_cache, send_anomaly_emails, send_ranking_emails
from .facebook import facebook
from .google import google
from .user import user

# Flask App Factory Pattern
def create_app(settings_override=None):
    app = Flask(__name__)
    CORS(app)

    # Conditionally load config based on env
    if os.environ.get('FLASK_ENV') == 'development':
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)

    if settings_override:
        app.config.update(settings_override)

    # Auth and DB models for firebase app
    if (not len(firebase_admin._apps)):
        cred = credentials.Certificate(app.config['SERVICE_ACCOUNT'])
        firebase_admin.initialize_app(cred)

    app.extensions["db"] = firestore.client()
    app.extensions["auth"] = firebase_admin.auth.Client(
        app=firebase_admin.get_app())
    
    # Index time route for testing
    @app.route('/')
    def get_current_time(): # pylint: disable=unused-variable
        return {'time': time.time(), 'revision': app.config["CLOUD_RUN_REVISION"]}

    @app.route('/keep_alive')
    def keep_alive(): # pylint: disable=unused-variable
        print("Polled app to keep it alive and avoid cold start problem.")
        return 'ok', 200

    @app.route('/send_email')
    def send_email():  # pylint: disable=unused-variable
        from fathom.lib import send_test_email
        email = request.args.get('email')
        if not email:
            return {"error": "Please add an email parameter"}
        print("Sending an email to {email}.")
        return send_test_email(email)

    @app.route('/send_rankings')
    def send_rankings():
        arguments = ['testing', 'do_not_actually_send']
        params = parse_params(request, arguments)
        actually_send = True
        if ('do_not_actually_send' in params):
            actually_send = False

        if "testing" in params:
            if actually_send:
                send_ranking_emails(testing=True, actually_send=actually_send)
            else:
                return send_ranking_emails(testing=True, actually_send=actually_send)
        else:
            send_ranking_emails(testing=False, actually_send=actually_send)
        return 'ok'

    @app.route('/send_anomalies')
    def send_anomalies():
        arguments = ['testing', 'do_not_actually_send', 'date_to_process']
        params = parse_params(request, arguments)
        date_to_process = None
        if ('date_to_process' in params):
            date_to_process = params['date_to_process']
        
        actually_send = True
        if ('do_not_actually_send' in params):
            actually_send = False

        if "testing" in params:
            if actually_send:
                send_anomaly_emails(testing=True, actually_send=actually_send, date_to_process=date_to_process)
            else:
                return send_anomaly_emails(testing=True, actually_send=actually_send, date_to_process=date_to_process)
        else:
            send_anomaly_emails(testing=False, date_to_process=date_to_process)
        return 'ok'

    @app.route('/cache_benchmarks')
    def cache_benchmarks():  # pylint: disable=unused-variable
        return get_benchmarks_cache()

    # get all routes
    @app.route('/routes')
    def routes(): # pylint: disable=unused-variable
        print("Return a list of routes.")
        output = []
        for rule in app.url_map.iter_rules():

            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            line = f"{rule.endpoint:50s} {methods:20s} {urllib.parse.unquote(url)}"
            print(line)

            output.append(line)
        return jsonify(sorted(output))

    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(facebook, url_prefix='/facebook')
    app.register_blueprint(google, url_prefix='/google')

    # Set up logging
    app.logger.setLevel(app.config['LOG_LEVEL'] or "INFO") # pylint: disable=no-member

    return app