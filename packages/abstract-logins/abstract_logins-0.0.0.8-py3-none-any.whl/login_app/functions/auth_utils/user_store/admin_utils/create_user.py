#!/usr/bin/env python3
"""
create_user.py  (updated to use `user_store.py` + your abstract‐database modules)
"""
# create_user.py

from abstract_utilities import SingletonMeta
from pathlib import Path
from dotenv import load_dotenv
import os,argparse,time,sys
LOG_FILE_PATH = "user_creation.log"  # wherever you want to keep your plaintext‐audit log
def append_log(username: str, plaintext_password: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE_PATH, "a", encoding="utf8") as f:
        f.write(f"[{ts}] {username} → {plaintext_password}\n")
class get_abstract_gui(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            import PySimpleGUI as sg
            self.sg=sg
class get_user_store(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            from .user_store import ensure_users_table_exists,get_user, add_or_update_user, verify_password,get_existing_users
            self.get_user = get_user
            self.add_or_update_user = add_or_update_user
            self.get_existing_users = get_existing_users
            self.ensure_users_table_exists = ensure_users_table_exists
            self.add_or_update_user = add_or_update_user
            self.verify_password = verify_password
          


        
# ────────────────────────────────────────────────────────────────────────────────
# (You can keep your existing PySimpleGUI layout, blinking logic, etc.)
# Just replace calls to the old user_db with get_user(), add_or_update_user(), verify_password()

def admin_login_prompt():
    simpleGui_mgr = get_abstract_gui()
    sg = simpleGui_mgr.sg
    userStore_mgr = get_user_store()
    get_user = userStore_mgr.get_user
    verify_password = userStore_mgr.verify_password
    layout = [
        [sg.Text("Administrator Login", font="Any 14")],
        [sg.Text("Username:", size=(12, 1)), sg.Input(key="--ADMIN_USER--")],
        [sg.Text("Password:", size=(12, 1)), sg.Input(key="--ADMIN_PASS--", password_char="*")],
        [sg.Button("Login"), sg.Button("Cancel")]
    ]
    win = sg.Window("Admin Authentication Required", layout, modal=True, finalize=True)

    while True:
        event, values = win.read()
        if event in (None, "Cancel"):
            win.close()
            return None
        if event == "Login":
            admin_user = values["--ADMIN_USER--"].strip()
            admin_pass = values["--ADMIN_PASS--"]
            if not admin_user or not admin_pass:
                sg.popup_error("Both fields are required.", title="Login Failed")
                continue

            row = get_user(admin_user)
            if not row:
                sg.popup_error("Admin user not found.", title="Login Failed")
                continue

            if not row["is_admin"]:
                sg.popup_error("User is not an administrator.", title="Access Denied")
                continue

            if not verify_password(admin_pass, row["password_hash"]):
                sg.popup_error("Incorrect password.", title="Login Failed")
                continue

            win.close()

            
            return admin_user

    # unreachable
    win.close()
    return None


def user_management_window(admin_username: str):
    # We already called ensure_users_table_exists() at import time, so the table is guaranteed to exist.
    
    # We can just do: SELECT username FROM users ORDER BY username via DatabaseManager or use get_user() in a loop.
    # But since we only provided get_user(username) above, let’s just do a quick query:
    simpleGui_mgr = get_abstract_gui()
    sg = simpleGui_mgr.sg
    userStore_mgr = get_user_store()
    get_user = userStore_mgr.get_user
    add_or_update_user = userStore_mgr.add_or_update_user
    get_existing_users = userStore_mgr.get_existing_users
    existing_users = get_existing_users()
    combo_choices = ["<New User>"] + existing_users

    layout = [
        [sg.Text(f"Logged in as admin: {admin_username}", font="Any 12")],
        [sg.Text("Select User:"), sg.Combo(combo_choices,
                                           default_value="<New User>",
                                           key="--USER_SELECT--",
                                           readonly=True,
                                           enable_events=True)],
        [sg.Text("Username:"), sg.Input(default_text="", key="--USERNAME--")],
        [sg.Text("Password:"), sg.Input(default_text="", key="--PASSWORD--", password_char="*")],
        [sg.Checkbox("Admin User?", key="--IS_ADMIN--", default=False)],
        [sg.Button("GeneratePassword", key="--RANDOM_PASSWORD--")],
        [sg.Button("OK"), sg.Button("Cancel")]
    ]

    window = sg.Window("User Manager (Postgres via AbstractDB)", layout, finalize=True)
    blinking = False
    blink_count = 0
    max_blinks = 6
    next_toggle_time = 0.0

    while True:
        event, values = window.read(timeout=100)
        now = time.time()

        # A) Combo selection changed
        if event == "--USER_SELECT--":
            chosen = values["--USER_SELECT--"]
            if chosen == "<New User>":
                window["--USERNAME--"].update(value="")
                window["--PASSWORD--"].update(value="")
                window["--IS_ADMIN--"].update(value=False)
            else:
                row = get_user(chosen)
                window["--USERNAME--"].update(value=chosen)
                window["--PASSWORD--"].update(value="")  # don’t show hash
                window["--IS_ADMIN--"].update(value=(row["is_admin"] if row else False))

        # B) Close / Cancel
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            break

        # C) Generate a strong random password
        if event == "--RANDOM_PASSWORD--":
            import secrets, string
            alphabet = string.ascii_letters + string.digits + string.punctuation
            while True:
                pwd = "".join(secrets.choice(alphabet) for _ in range(16))
                if (
                    any(c.islower() for c in pwd)
                    and any(c.isupper() for c in pwd)
                    and any(c.isdigit() for c in pwd)
                    and any(c in string.punctuation for c in pwd)
                ):
                    break
            window["--PASSWORD--"].update(value=pwd)

        # D) OK button clicked
        if event == "OK":
            user_input = values["--USERNAME--"].strip()
            pwd_input = values["--PASSWORD--"]
            is_admin_flag = values["--IS_ADMIN--"]

            if not user_input:
                blinking = True
                blink_count = 0
                window["--USERNAME--"].update(background_color="red")
                window.refresh()
                next_toggle_time = now + 0.3
                continue

            existing_row = get_user(user_input)
            if existing_row is None:
                # New user
                if not pwd_input:
                    blinking = True
                    blink_count = 0
                    window["--PASSWORD--"].update(background_color="red")
                    window.refresh()
                    next_toggle_time = now + 0.3
                    continue

                add_or_update_user(username=user_input,
                                   plaintext_pwd=pwd_input,
                                   is_admin=is_admin_flag)
                append_log(user_input, pwd_input)
                sg.popup_ok(f"New user '{user_input}' created. Admin={is_admin_flag}")
                break

            else:
                # Existing user
                if not pwd_input:
                    # No password typed → preserve old hash but update is_admin
                    add_or_update_user(username=user_input,
                                       plaintext_pwd=existing_row["password_hash"],
                                       is_admin=is_admin_flag)
                    sg.popup_ok(f"Updated user '{user_input}'. Admin={is_admin_flag}")
                    break
                else:
                    # Overwrite both hash and is_admin
                    add_or_update_user(username=user_input,
                                       plaintext_pwd=pwd_input,
                                       is_admin=is_admin_flag)
                    append_log(user_input, pwd_input)
                    sg.popup_ok(f"User '{user_input}' updated. Admin={is_admin_flag}")
                    break

        # E) Blinking logic
        if blinking and now >= next_toggle_time:
            if blink_count % 2 == 0:
                window["--USERNAME--"].update(background_color="white")
                window["--PASSWORD--"].update(background_color="white")
            else:
                window["--USERNAME--"].update(background_color="red")
                window["--PASSWORD--"].update(background_color="red")
            window.refresh()

            blink_count += 1
            next_toggle_time = now + 0.3

            if blink_count >= max_blinks:
                blinking = False
                window["--USERNAME--"].update(background_color="white")
                window["--PASSWORD--"].update(background_color="white")
                window.refresh()

    window.close()


def edit_users():
    import PySimpleGUI as sg

    # ───────────────────────────────────────────────────────────────────────────
    # Load environment variables from the .env file that lives in this same folder:

    # Now os.environ["SOLCATCHER_DATABASE_HOST"], etc. will be populated.
    # ───────────────────────────────────────────────────────────────────────────
    # (The rest of create_user.py remains exactly as before…)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize the Postgres schema (create 'users' table) and exit."
    )
    args = parser.parse_args()

    if args.init_db:
        # Headless: create the table and trigger, then exit
        ensure_users_table_exists = get_user_store().ensure_users_table_exists
        try:
            ensure_users_table_exists()
            print("✅ Schema initialized successfully (Postgres 'users' table created).")
        except Exception as e:
            print("✘ Error initializing schema:", e)
            sys.exit(1)
        sys.exit(0)

    sg.theme("DarkBlue14")

    admin_user = admin_login_prompt()
    if not admin_user:
        print("✘ Administrator login failed or cancelled. Exiting.")
        sys.exit(1)

    user_management_window(admin_user)


