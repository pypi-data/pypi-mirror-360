from flask import Flask, request
from flask_cors import CORS
import os
import logging
from .imports import *
from flask_cors import CORS
from .endpoints import(secure_logout_bp,
                    secure_login_bp,
                    change_passwords_bp,
                    secure_users_bp,
                    secure_settings_bp,
                    secure_views_bp,
                    secure_chat_bp,
                    secure_files_bp
                    )
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def login_app():
    app = Flask(
        __name__,
        static_folder=STATIC_FOLDER,
        static_url_path=URL_PREFIX
    )
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    CORS(app, resources={r"/secure-files/*": {"origins": "*", "supports_credentials": True}})

    @app.before_request
    def log_request():
        logger.debug(f"Request: {request.method} {request.path} {request.form} {request.files}")

    app.register_blueprint(secure_users_bp)
    app.register_blueprint(secure_logout_bp)
    app.register_blueprint(secure_login_bp)
    app.register_blueprint(change_passwords_bp)

    app.register_blueprint(secure_settings_bp)
    app.register_blueprint(secure_files_bp)

    app.register_blueprint(secure_chat_bp)

    app.register_blueprint(secure_views_bp)
    


    return app
