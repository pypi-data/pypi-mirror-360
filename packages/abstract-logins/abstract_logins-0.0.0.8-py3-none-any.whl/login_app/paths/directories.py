from .static_dir import *
ABS_HTML_AUTHS_FOLDER = get_html_path('auths')
URL_PREFIX = ABS_URL_PREFIX
STATIC_FOLDER = ABS_STATIC_DIR
UPLOAD_FOLDER = ABS_UPLOAD_DIR
ABS_PUBLIC_FOLDER = ABS_PUBLIC_DIR
ABS_UPLOAD_ROOT = "/var/www/abstractendeavors/secure-files/uploads"
def get_rel_path(path,rel_path):
    rel_path = os.path.relpath(path, rel_path)
    return rel_path
def get_rel_uploads_path(path):
    rel_path = get_rel_path(path, ABS_UPLOAD_ROOT)
    return rel_path


