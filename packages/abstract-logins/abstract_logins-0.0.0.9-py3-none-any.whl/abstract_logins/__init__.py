from .imports import *

from .endpoints import(
    secure_limiter,
    secure_logout_bp,
    secure_login_bp,
    change_passwords_bp,
    secure_users_bp,
    secure_settings_bp,
    secure_views_bp,
    secure_download_bp,
    secure_upload_bp,
    secure_files_bp,
    secure_remove_bp,
    secure_env_bp

)






def login_app():
    app = Flask(
        __name__,
        static_folder=STATIC_FOLDER,
        static_url_path=URL_PREFIX
    )
    app.url_map.strict_slashes = False
    secure_limiter.init_app(app)
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    CORS(
        app,
        resources={r"/secure-files/.*": {"origins": "*"}},  # regex + wildcard origin
        supports_credentials=True                           # <-- top-level
    )
    # 2) put your download logging in the download view itself
    @app.before_request
    def log_request():
        # this logs *every* request; you can move it into download_file() if you like
        app.logger.debug(
            f"{request.method} {request.path} "
            f"form={dict(request.form)} files={list(request.files)}"
        )
    app.config.update({
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "None",   # allow cross-site if your front-end is on a different origin
        "SESSION_COOKIE_SECURE": True        # only send over HTTPS
    })

    app = addHandler(app,name='download_audit')
    app.register_blueprint(secure_users_bp)
    app.register_blueprint(secure_logout_bp)
    app.register_blueprint(secure_login_bp)
    app.register_blueprint(change_passwords_bp)

    app.register_blueprint(secure_settings_bp)
    app.register_blueprint(secure_files_bp)
    app.register_blueprint(secure_upload_bp)
    app.register_blueprint(secure_download_bp)

    app.register_blueprint(secure_views_bp)
    app.register_blueprint(secure_remove_bp)
    app.register_blueprint(secure_env_bp)

    return app
