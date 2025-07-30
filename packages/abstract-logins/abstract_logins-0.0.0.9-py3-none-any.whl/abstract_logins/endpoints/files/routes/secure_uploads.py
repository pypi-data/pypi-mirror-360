from ...imports import *
import os


secure_upload_bp,logger = get_bp(
    "secure_upload_bp",
    __name__,
    url_prefix=URL_PREFIX       # <-- everything in this Blueprint sits under /secure-files
)


@secure_upload_bp.route("/upload", methods=["POST"])
@secure_upload_bp.route("/upload/<path:rel_path>", methods=["GET"])
@login_required
def upload_file(rel_path: str | None = None):
    initialize_call_log()

    user_name = request.user["username"]
    if not user_name:
        return jsonify(message="Missing user_name"), 400

    if "file" not in request.files:
        return jsonify(message="No file provided"), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify(message="No file selected"), 400

    filename       = secure_filename(file.filename)
    subdir         = get_safe_subdir(request) or ""
    user_upload_dir = get_user_upload_dir(request, user_name)
    target_dir      = os.path.join(user_upload_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)

    full_path = os.path.join(target_dir, filename)
    file.save(full_path)

    rel_path  = os.path.relpath(full_path, ABS_UPLOAD_ROOT)
    file_id   = insert_any_combo(
        table_name="uploads",
        insert_map=dict(
            filename       = filename,
            filepath       = rel_path,
            uploader_id    = user_name,
            shareable      = request.form.get("shareable", False),
            download_count = request.form.get("download_count", 0),
            download_limit = request.form.get("download_limit"),
            share_password = request.form.get("share_password"),
        ),
        returning="id",
    )

    return jsonify(
        message        = "File uploaded successfully.",
        filename       = filename,
        filepath       = rel_path,
        file_id        = file_id,
        uploader_id    = user_name,
    ), 200

