from flask import Response,render_template
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ...imports import *
secure_download_bp, logger = get_bp(
    "secure_download",
    __name__,
    static_folder=STATIC_FOLDER,
    url_prefix=URL_PREFIX
)

def get_file_inits(req, file_id=None):
    request_data = extract_request_data(req)
    data = request_data.get('json', {}) or {}
    args = request_data.get('args', [])

    logger.info(request_data)
    username = get_user_name(req=req)

    # build your search_map as before…
    search_map = {}
    if 'rel_path' in data:
        search_map['rel_path'] = data['rel_path']
    if file_id or data.get('id') or data.get('file_id'):
        search_map['id'] = int(file_id or data.get('id') or data.get('file_id'))
    if not search_map:
        return get_json_call_response('Missing file path and id.', 400)

    # **HERE**: grab the password from JSON **or** query **or** form POST
    pwd_given = (
        data.get('pwd')
        or req.args.get('pwd')
        or (req.form.get('pwd') if req.method == 'POST' else None)
    )

    return search_map, pwd_given, username

def add_to_download_count(search_map):
    if not isinstance(search_map,dict):
        if is_number(search_map):
            search_map = {"id":search_map}
    columnName = ["download_count","download_limit"]
    result = fetch_any_combo(column_names=columnName,
                                 table_name='uploads',
                                 search_map=search_map)
    download_count = result[0].get(columnName[0])
    download_limit = result[0].get(columnName[1])
    new_count = int(download_count) + 1
    if download_limit and new_count > download_limit:
        return 'Download limit reached.'
   
    update_any_combo(table_name='uploads',
                                  update_map={columnName[0]:new_count},
                                  search_map=search_map)

    return new_count
def get_path_and_filename(filepath):
    abs_path = os.path.join(ABS_UPLOAD_DIR, filepath)
    if not os.path.isfile(abs_path):
        return False,'File missing on disk.'
    basename = os.path.basename(abs_path)
    filename,ext = os.path.splitext(basename)
    return abs_path,filename



def check_password(pwd_given: Optional[str], share_password: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Returns (ok, error_code):
      ok=True  → password not required or was correct
      ok=False → password required or incorrect; error_code tells which
    """
    # No password set on the file → always OK
    if not share_password:
        return True, None

    # Password *is* required
    if not pwd_given:
        return False, 'PASSWORD_REQUIRED'

    # Password *was* provided, but wrong
    if not verify_password(pwd_given, share_password):
        return False, 'PASSWORD_INCORRECT'

    # All good
    return True, None
    
def get_download(req,file_id=None):
    search_map,pwd_given,username = get_file_inits(req,file_id=file_id)
    column_names = ['uploader_id','shareable','filepath','share_password']
    # fetch metadata
    row = fetch_any_combo(column_names='*',
                                 table_name='uploads',
                         search_map=search_map)
    logger.info(row)
    if not row:
        return get_json_call_response('File not found.', 404)
    if len(row) == 1:
        row = row[0]
    uploader_id = row['uploader_id']
    is_user = uploader_id == username
    shareable = row['shareable']
    logger.info(f"shareable={shareable}")
    if shareable == False and not is_user:
        return None, None, 'NOT_SHAREABLE'
    filepath = row['filepath']
    # optional password check, limit check, increment count…
    abs_path,filename = get_path_and_filename(filepath)
    if not abs_path:
        return None, None, 'NO_FILE_FOUND'
    share_password = row['share_password']
    ok, err = check_password(pwd_given, share_password)
    if not ok:
        return None, None, err
    new_count = add_to_download_count(search_map)
    if not isinstance(new_count, int):
        return None, None, 'DOWNLOAD_LIMIT'
    return abs_path, filename, None

@secure_download_bp.route('/download', methods=['POST'])
@login_required
def downloadFile():
    initialize_call_log()
    abs_path,filename = get_download(request)
    if isinstance(filename,int):
        return get_json_call_response(abs_path, filename)
    return send_file(
        abs_path,
        as_attachment=True,
        download_name=filename)

@secure_download_bp.route('/secure-download/<path:file_id>', methods=['GET','POST'])
def download_file(file_id=None):
    initialize_call_log()
    abs_path,filename,err = get_download(request,file_id=file_id)
    if err == 'PASSWORD_REQUIRED':
        return render_template('enter_password.html', file_id=file_id), 200
    if err == 'PASSWORD_INCORRECT':
        return render_template('enter_password.html', file_id=file_id, error='Incorrect password.'), 401
    if err == 'DOWNLOAD_LIMIT':
        return get_json_call_response('Download limit reached.', 403)
    if err == 'NO_FILE_FOUND':
        return get_json_call_response('no file found.', 403)
    if err == 'NOT_SHAREABLE':
        return get_json_call_response('not sharable', 403)
    if isinstance(filename,int):
        return get_json_call_response(abs_path, filename)
    return send_file(
        abs_path,
        as_attachment=True,
        download_name=filename
        )

secure_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
@secure_download_bp.route("/secure-download/token/<token>")
@secure_limiter.limit("10 per minute")
@login_required
def download_with_token(token):
    initialize_call_log()
    try:
        data = decode_token(token)
    except jwt.ExpiredSignatureError:
        return get_json_call_response("Download link expired.", 410)
    except jwt.InvalidTokenError:
        return get_json_call_response("Invalid download link.", 400)
    # Check that the token’s user matches the logged-in user
    if data["sub"] != get_user_name(request):
        return get_json_call_response("Unauthorized.", 403)
    # Then serve exactly like before, using data["path"]
    return _serve_file(data["path"])

def _serve_file(rel_path: str):
    # after all your checks…
    internal_path = f"/protected/{rel_path}"
    resp = Response(status=200)
    resp.headers["X-Accel-Redirect"] = internal_path
    # optionally set download filename:
    resp.headers["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(rel_path)}"'
    )
    return resp
