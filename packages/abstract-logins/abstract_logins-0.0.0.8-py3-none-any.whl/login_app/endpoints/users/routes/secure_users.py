# /flask_app/login_app/endpoints/users/routes.py
from ....imports import *   # brings in: get_bp, login_required, get_request_data, get_user, verify_password,
                         # add_or_update_user, generate_token, get_json_call_response, initialize_call_log, etc.

secure_users_bp, logger = get_bp(
    "secure_users_bp",
    __name__,
    static_folder=STATIC_FOLDER,
    url_prefix=URL_PREFIX
)

@secure_users_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    initialize_call_log()
    try:
        users = get_existing_users()
    except Exception as e:
        return get_json_call_response(
            value={"error": "Unauthorized user"},
            status_code=500,
            logMsg=f"Error fetching users: {e}"
        )

    return get_json_call_response(value=users,
                                  status_code=200)









