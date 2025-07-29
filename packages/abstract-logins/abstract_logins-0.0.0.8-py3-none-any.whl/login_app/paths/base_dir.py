import os
WWW_DIR="/var/www/"
BASE_DIR = os.path.join(WWW_DIR, "abstractendeavors")
ABS_URL_PREFIX = "/secure-files/"
ABS_BASE_DIR = os.path.join(BASE_DIR, "secure-files")
def get_base_path(path):
    base_dir = os.path.join(ABS_BASE_DIR, path)
    return base_dir
