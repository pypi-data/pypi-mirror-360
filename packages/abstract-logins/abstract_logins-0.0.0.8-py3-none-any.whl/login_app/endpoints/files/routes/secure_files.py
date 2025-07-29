# /flask_app/login_app/endpoints/files/secure_files.py
from ....imports import *
import glob
from flask import send_file
from abstract_ocr.functions import generate_file_id
# Correct get_bp signature:  get_bp(name, *, url_prefix=None, static_folder=None)
secure_files_bp, logger = get_bp(
    "secure_files_bp",
    __name__,
    url_prefix=URL_PREFIX,
    static_folder = STATIC_FOLDER
)
ABS_UPLOAD_ROOT = "/var/www/abstractendeavors/secure-files/uploads"


@secure_files_bp.route("/list", methods=["POST"])
@login_required
def list_files():
    user_name = get_user_name(req=request)
    items = get_upload_items(
        req=request,
        user_name=user_name,
        include_untracked=False   # ← skip the FS-scan on your "initial" list call
    )
    return jsonify({"files": items})
@secure_files_bp.route('/download', methods=['GET'])
@login_required
def download_file():
    initialize_call_log()
    username = request.user['username']
    try:
        rows = select_rows(
            'SELECT id, filename, filepath, shareable, share_password, download_count, download_limit, uploader_id '
            'FROM uploads WHERE filepath = %s',
            (rel_path,)
        )
        if not rows:
            return get_json_call_response('File not found.', 404)
        row = rows[0]
    except Exception as e:
        return get_json_call_response('Database error.', 500, logMsg=f'DB error in download_file: {e}')

    if not row['shareable'] and row['uploader_id'] != username:
        return get_json_call_response('This file is not shareable.', 403)

    pwd_given = request.args.get('pwd')
    if row['share_password']:
        if not pwd_given:
            form_html = (
                '<html><body>'
                '<h3>Enter password to download:</h3>'
                '<form method="GET">'
                '  <input type="password" name="pwd" />'
                '  <button type="submit">Download</button>'
                '</form>'
                '</body></html>'
            )
            return form_html, 200
        if not verify_password(pwd_given, row['share_password']):
            return get_json_call_response('Incorrect password.', 401)

    if row['download_limit'] is not None and row['download_count'] >= row['download_limit']:
        return get_json_call_response('Download limit reached.', 410)

    try:
        insert_query(
            'UPDATE uploads SET download_count = download_count + 1 WHERE id = %s',
            (row['id'],)
        )
    except Exception as e:
        unified.logger.error(f'DB error incrementing download_count: {e}')

    absolute_path = os.path.join(ABS_UPLOAD_FOLDER, row['filepath'])
    if not os.path.isfile(absolute_path):
        return get_json_call_response('File not found on disk.', 404)

    return send_file(absolute_path, as_attachment=True, download_name=row['filename'])

@secure_files_bp.route('/files/<int:file_id>/share-link', methods=['GET', 'POST',"PATCH"])
@login_required
def generateShareLink():
    initialize_call_log()
    username = request.user['username']
    data = parse_and_spec_vars(request,['file_id'])
    file_id = data.get('file_id')
    try:
        rows = select_rows(
            'SELECT shareable FROM uploads WHERE id = %s AND uploader_id = %s',
            (file_id, username)
        )
        if not rows:
            return get_json_call_response('File not found.', 404)
        if not rows[0]['shareable']:
            return get_json_call_response('File is not shareable.', 403)
    except Exception as e:
        return get_json_call_response('Database error.', 500, logMsg=f'DB error in generate_share_link: {e}')

    host = request.host_url.rstrip('/')
    share_url = f'{host}/secure-files/download/{file_id}'
    return get_json_call_response(share_url, 200)


@secure_files_bp.route('/files/<int:file_id>/share', methods=['PATCH'])
@login_required
def updateShareSettings():
    """
    PATCH /secure-files/files/<file_id>/share
    Body JSON: { shareable: bool, share_password: (string|null), download_limit: (int|null) }
    Only the owner may update. If shareable=false, clears password & limit & resets count.
    If shareable=true, optionally hashes share_password and sets download_limit.
    """
    user_id = get_jwt_identity()
    data = parse_and_spec_vars(request,['file_id','shareable','share_password','download_limit'])
    file_id = data.get('file_id')
    # Validate inputs
    shareable     = bool(data.get('shareable', False))
    pwd_plain     = data.get('share_password')      # string or None
    download_lim  = data.get('download_limit')      # int or None

    # 1) Fetch existing row to confirm ownership and get current download_count
    try:
        query="""
            SELECT uploader_id, download_count
              FROM uploads
             WHERE id = %s
        """, 
        row = select_rows(query,(file_id,))
        if row is None:
            return get_json_call_response(value="File not found.",
                                          logMsg=f"DB error in update_share_settings (fetch): {e}",
                                          status_code=404)
        user_value = row.get("uploader_id")
        if user_value != user_id:
            return get_json_call_response(value="Not authorized.",
                                          logMsg="File is not shareable.",
                                          status_code=403)
        current_download_count = row["download_count"]
    except Exception as e:
        return get_json_call_response(value="Database error.",
                                      logMsg=f"DB error in update_share_settings (fetch): {e}",
                                      status_code=500)


    # 2) Decide on new column values
    new_shareable     = shareable
    new_pass_hash     = None
    new_download_limit = None
    new_download_count = current_download_count

    if not new_shareable:
        # Disabling sharing → clear everything
        new_download_count = 0
        new_download_limit = None
        new_pass_hash      = None
    else:
        # Enabling sharing → maybe hash the new password
        if isinstance(pwd_plain, str) and pwd_plain.strip():
            new_pass_hash = bcrypt.hashpw(pwd_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # If download_lim is a positive integer, use it; else treat as unlimited
        try:
            if download_lim is not None and int(download_lim) > 0:
                new_download_limit = int(download_lim)
        except (ValueError, TypeError):
            new_download_limit = None

    # 3) Perform the UPDATE
    try:
        query = """
            UPDATE uploads
               SET shareable      = %s,
                   share_password = %s,
                   download_limit = %s,
                   download_count = %s
             WHERE id = %s
        """
        args = (
            
        )
        insert_query(query, new_shareable,
                            new_pass_hash,
                            new_download_limit,
                            new_download_count,
                            file_id)

    except Exception as e:
        return get_json_call_response(value="Unable to update share settings.",
                                          logMsg=f"DB error in update_share_settings (update): {e}",
                                          status_code=500)

    return get_json_call_response(value="Share settings updated.",
                                      status_code=200)


@secure_files_bp.route('/files/<int:file_id>/share-link', methods=['GET','POST'])
@login_required
def generate_share_link():
    """
    POST /secure-files/files/<file_id>/share-link
    Confirms the file belongs to this user AND is shareable, then returns JSON { share_url: <url> }.
    """
    initialize_call_log()
    user_id = get_jwt_identity()
    kwargs = parse_and_spec_vars(request,['file_id'])
    file_id = kwargs.get('file_id')
    # 1) Verify ownership and shareable flag
    try:
        query="""
            SELECT shareable
              FROM uploads
             WHERE id = %s AND uploader_id = %s
        """, 
        row = select_rows(query,file_id, user_id)
        if row is None:
            return get_json_call_response(value ="File not found.",
                                          logMsg="File not found.",
                                          status_code=404)
        if not row.get("shareable"):
            return get_json_call_response(value="File is not shareable.",
                                          logMsg="File is not shareable.",
                                          status_code=403)
    
       
    except Exception as e:
        return get_json_call_response(value="Database error.",
                                      logMsg=f"DB error in generate_share_link: {e}",
                                      status_code=500)

    # 2) Build the share URL (simply using the numeric ID as token)
    host = request.host_url.rstrip('/')
    share_url = f"{host}/secure-files/download/{file_id}"
    return get_json_call_response(value=share_url, status_code=200)
@secure_files_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    initialize_call_log()
    user_name = get_user_name(req=request)
    if not user_name:
        logger.error("Missing user_name")
        return jsonify({"message": "Missing user_name"}), 400

    if 'file' not in request.files:
        logger.error(f"No file in request.files: {request.files}")
        return jsonify({"message": "No file provided."}), 400

    file = request.files['file']
    if not file or not file.filename:
        logger.error("No file selected or empty filename")
        return jsonify({"message": "No file selected."}), 400

    filename = secure_filename(file.filename)
    if not filename:
        logger.error("Invalid filename after secure_filename")
        return jsonify({"message": "Invalid filename."}), 400
    kwargs = parse_and_spec_vars(request,['shareable','download_count','download_limit','share_password'])
    shareable = kwargs.get('shareable',False)
    download_count = kwargs.get('download_count',0)
    download_limit = kwargs.get('download_limit',None)
    share_password = kwargs.get('share_password',False)
    user_upload_dir = get_user_upload_dir(req=request, user_name=user_name)
    safe_subdir = get_safe_subdir(req=request) or ''
    user_upload_subdir = os.path.join(user_upload_dir, safe_subdir)
    os.makedirs(user_upload_subdir, exist_ok=True)
    full_path = os.path.join(user_upload_subdir, filename)
    logger.info(f"Received: file={filename}, subdir={safe_subdir}")
    file.save(full_path)
    rel_path = os.path.relpath(full_path, ABS_UPLOAD_ROOT)
    file_id = create_file_id(
                        filename=filename,
                        filepath=rel_path,
                        uploader_id= user_name,
                        shareable=shareable or False,
                        download_count=download_count or 0,
                        download_limit=download_limit or None,
                        share_password=share_password or False,
                    )
    




    return jsonify({
            "message": "File uploaded successfully.",
            "filename": filename,
            "filepath": rel_path,
            "file_id": file_id,
            "uploader_id": user_name,
            "shareable": shareable,
            "download_count": download_count,
            "download_limit": download_limit,
            "share_password": share_password,
        }), 200
