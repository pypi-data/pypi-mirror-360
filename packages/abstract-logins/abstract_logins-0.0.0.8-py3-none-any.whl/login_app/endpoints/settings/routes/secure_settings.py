# /var/www/abstractendeavors/secure-files/big_man/flask_app/login_app/routes.py
from ....imports import *
# ──────────────────────────────────────────────────────────────────────────────
# 2) Hard‐code the absolute path to your “public/” folder, where index.html, login.html, main.js live:
# Make a folder named “uploads” parallel to “public”:

secure_settings_bp, logger = get_bp('secure_settings_bp',
                                    __name__,
                                    url_prefix=URL_PREFIX,
                                    static_folder = STATIC_FOLDER)
def get_all_key_unfos(req):
    keys =["created_at",
           "download_count",
           "download_limit",
           "filename",
           "filepath",
           "fullpath",
           "id",
           "share_password",
           "shareable",
           "uploader_id",
           "is_shareable",
           "needsPassword",
           "downloadPassword",
           "max_downloads"]           
    username = req.user['username']
    data = parse_and_spec_vars(req,keys)
    created_at = data.get("created_at",datetime.utcnow())
    download_count = data.get("download_count",0)
    download_limit = data.get("download_limit",None)
    filename = data.get("filename",None)
    filepath = data.get("filepath",None)
    fullpath = data.get("fullpath",None)
    file_id = data.get("id",None)
    share_password = data.get("share_password", None)
    shareable = data.get("shareable", False)
    uploader_id = data.get("uploader_id",username)
    is_shareable = data.get("is_shareable",False)
    needsPassword = data.get("needsPassword", False)
    downloadPassword = data.get("downloadPassword",None)
    max_downloads = data.get("max_downloads",None)


@secure_settings_bp.route("/settings/<path:rel_path>", methods=["POST","GET","PATCH"])
@login_required
def update_settings():
    """
    Expects JSON body:
      {
        "is_shareable":   <bool>,
        "downloadPassword": "<string>" or "",
        "maxDownloads":   <int> or null
      }
    Updates the file metadata for <rel_path> (relative to ABS_UPLOAD_FOLDER).
    """
    initialize_call_log()
    data = parse_and_spec_vars(request,['rel_path'])
    rel_path = data.get('rel_path')
    initialize_call_log(data=data)
    # Validate existence of those keys:
    if data is None:
        return get_json_call_response(value="Missing JSON body.", status_code=400)


    # Extract fields, providing defaults if not present:
    is_shareable = data.get("is_shareable", None)
    download_password = data.get("downloadPassword", None)
    max_downloads = data.get("maxDownloads", None)

    # You can choose to check types here if you like:
    if is_shareable is None or download_password is None or max_downloads is None:
        return get_json_call_response(value="Required fields: is_shareable, downloadPassword, maxDownloads.", status_code=400)
 

    # Now split rel_path into subdir / filename (to match how you store metadata)
    # e.g. if rel_path = "invoices/2025-01-01.pdf", then:
    import os

    subdir = ""
    filename = rel_path
    if "/" in rel_path:
        parts = rel_path.split("/")
        subdir = "/".join(parts[:-1])
        filename = parts[-1]

    username = request.user["username"]  # from @login_required

    # At this point, you need to call whatever database‐layer you have to update
    # the “files” table (or JSON, etc.). For example, if you have a function like:
    #   fileDb.updateFileSettings(owner, filename, subdir, { … })
    # then do something like:
    try:
        # Suppose you have a `fileDb.updateFileSettings` API (as in your Node example).
        # Here’s pseudocode—replace with your actual data‐store call:
        fileDb.updateFileSettings(
            owner=username,
            filename=filename,
            subdir=subdir,
            settings={
                "is_shareable": bool(is_shareable),
                # if downloadPassword is the empty string → clear the password;
                # otherwise hash & store it. (Implement as your DB/utility expects.)
                "downloadPassword": download_password.strip(),
                # If maxDownloads is None or 0 → interpret as unlimited, else store int.
                "max_downloads": None if (max_downloads is None or max_downloads == 0) else int(max_downloads),
            },
        )
    except Exception as e:
        # Log or inspect e as needed
        return get_json_call_response(value="Server Error; Settings Not Updated", status_code=500,logMsg=f"{e}")


    return get_json_call_response(value="Settings updated.", status_code=200)

@secure_settings_bp.route('/settings', methods=['POST',"GET","PATCH"])
@login_required
def updateSettings():
    initialize_call_log()
    data = request.get_json()
    if not data:
        return get_json_call_response('Missing JSON body.', 400)
    username = request.user['username']
    is_shareable = data.get('is_shareable')
    download_password = data.get('downloadPassword')
    max_downloads = data.get('maxDownloads')
    
    if is_shareable is None or download_password is None or max_downloads is None:
        return get_json_call_response('Required fields: is_shareable, downloadPassword, maxDownloads.', 400)

    username = request.user['username']
    try:
        rows = select_rows(
            'SELECT id, uploader_id FROM uploads WHERE filepath = %s',
            (rel_path,)
        )
        if not rows:
            return get_json_call_response('File not found.', 404)
        if rows[0]['uploader_id'] != username:
            return get_json_call_response('Not authorized.', 403)
        file_id = rows[0]['id']
    except Exception as e:
        return get_json_call_response('Database error.', 500, logMsg=f'DB error in update_settings: {e}')

    share_password = None
    if download_password.strip():
        share_password = bcrypt.hashpw(download_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    max_downloads = None if max_downloads == 0 else max_downloads
    try:
        insert_query(
            'UPDATE uploads SET shareable = %s, share_password = %s, download_limit = %s '
            'WHERE id = %s',
            (is_shareable, share_password, max_downloads, file_id)
        )
    except Exception as e:
        return get_json_call_response('Unable to update settings.', 500, logMsg=f'DB error in update_settings: {e}')

    return get_json_call_response('Settings updated.', 200)

@secure_settings_bp.route('/files/share', methods=['GET', 'PATCH'])
@login_required
def share_settings(file_id=None):
    """
    GET  /files/share?id=<file_id>             → return current share settings
    PATCH /files/share                         → accept JSON payload to update
    """
    user = request.user['username']

    # --- 1) Identify which file we're talking about ---
    #   Clients can send `?id=123` on GET, or include `id` in the JSON for PATCH.
    if request.method == 'GET':
        file_id = request.args.get('id', type=int)
    else:
        data = request.get_json() or {}
        file_id = data.get('id')

    if not file_id:
        return get_json_call_response('Missing file id.', 400)

    # --- 2) Fetch the existing record & enforce ownership ---
    row = select_rows(
        'SELECT uploader_id, shareable, share_password, download_limit, download_count '
        'FROM uploads WHERE id = %s',
        (file_id,)
    )
    if not row:
        return get_json_call_response('File not found.', 404)
    if row['uploader_id'] != user:
        return get_json_call_response('Not authorized.', 403)

    if request.method == 'GET':
        # Return exactly the fields the front end cares about
        return jsonify({
            'id':            file_id,
            'shareable':     row['shareable'],
            'download_limit': row['download_limit'],
            'share_password': bool(row['share_password']),
            'download_count': row['download_count'],
        }), 200

    # --- 3) PATCH: pull only the updatable keys from JSON ---
    payload = request.get_json() or {}
    shareable     = payload.get('shareable', row['shareable'])
    limit_raw     = payload.get('download_limit', row['download_limit'])
    pwd_plain     = payload.get('downloadPassword')   # front end name
    needs_password = bool(pwd_plain and pwd_plain.strip())

    # normalize download_limit
    try:
        download_limit = int(limit_raw) if limit_raw is not None else None
        if download_limit is not None and download_limit < 0:
            raise ValueError()
    except ValueError:
        return get_json_call_response('Invalid download_limit', 400)

    # hash password if needed
    if needs_password:
        pass_hash = bcrypt.hashpw(
            pwd_plain.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
    else:
        pass_hash = None

    # if shareable is being turned off, clear out limits & password
    if not shareable:
        download_limit = None
        pass_hash      = None

    # --- 4) Persist changes ---
    try:
        insert_query(
            """
            UPDATE uploads
               SET shareable      = %s,
                   share_password = %s,
                   download_limit = %s
             WHERE id = %s
            """,
            (shareable, pass_hash, download_limit, file_id)
        )
    except Exception as e:
        logger.error(f"DB error updating share settings: {e}")
        return get_json_call_response(
            'Unable to update share settings.',
            500,
            logMsg=f'DB error in update_share_settings: {e}'
        )

    return get_json_call_response('Share settings updated.', 200)
