from datetime import datetime
from abstract_flask import *
from ..auth_utils.query_utils import *
from ..paths import *
import glob
from abstract_utilities import get_logFile
logger = get_logFile('file_utils')

# Define metadata keys (example, adjust based on UPLOAD_ITEM_KEYS)
UPLOAD_ITEM_KEYS = {
    'filename': {'default': '', 'function': lambda path: os.path.basename(path)},
    'filepath': {'default': '', 'function': lambda path: path},
    'uploader_id': {'default': '', 'function': lambda req, user_name: user_name},
    'shareable': {'default': False},
    'download_count': {'default': 0},
    'download_limit': {'default': None},
    'share_password': {'default':False},
    'created_at': {'default': None},
}

def get_user_name(req=None,user_name=None):
    user_name = user_name or req.user["username"]
    return user_name
def get_user_upload_dir(req=None,user_name=None,user_upload_dir=None):
    user_name = user_name or get_user_name(req=req,user_name=user_name)
    user_upload_dir = user_upload_dir or os.path.join(ABS_UPLOAD_ROOT, str(user_name))
    os.makedirs(user_upload_dir,exist_ok=True)
    return user_upload_dir
def get_glob_files(req=None,user_name=None,user_upload_dir=None):
    user_upload_dir = get_user_upload_dir(req=req,user_name=user_name,user_upload_dir=user_upload_dir)
    pattern = os.path.join(user_upload_dir, "**/*")  # include all files recursively
    glob_files = glob.glob(pattern, recursive=True)
    return glob_files
def get_upload_items(
    req=None,
    user_name=None,
    user_upload_dir=None,
    include_untracked: bool = False
):
    # 1) build & run the query (all users if user_name is None)
    sql = """
        SELECT id, filename, filepath, uploader_id, shareable,
               download_count, download_limit, share_password, created_at
        FROM uploads
    """
    params = ()
    if user_name:
        sql += " WHERE uploader_id = %s"
        params = (user_name,)

    try:
        rows = select_distinct_rows(sql, (user_name,))  # now returns List[Dict]
    except Exception as e:
        print(f"Database error in get_upload_items: {e}")
        return []

    # 2) map each tuple to a dict via zip
    keys = ['id', 'filename', 'filepath', 'uploader_id',
            'shareable', 'download_count', 'download_limit',
            'share_password', 'created_at']
    files = []
    
    for row in rows:
        file = dict(row)     # safe, because row is already a dict
        file['fullpath'] = os.path.join(ABS_UPLOAD_ROOT, file['filepath'])
        files.append(file)

    # 3) optionally scan for untracked files (same as before)
    if include_untracked:
        glob_files = get_glob_files(req=req, user_name=user_name,
                                    user_upload_dir=user_upload_dir)
        for full_path in glob_files:
            if (os.path.isfile(full_path)
                and not any(f['filepath'] == full_path for f in files)
            ):
                new_file = {}
                for key, vals in UPLOAD_ITEM_KEYS.items():
                    val = vals.get('default')
                    fn  = vals.get('function')
                    if fn:
                        args = (full_path,) if key != 'uploader_id' else (req, user_name)
                        val = fn(*args)
                    new_file[key] = val
                new_file['id'] = create_file_id(**new_file)
                insert_untracked_file(new_file)
                files.append(new_file)

    return files
def insert_untracked_file(file):
    """Insert untracked filesystem file into uploads table."""

    query = """
        INSERT INTO uploads (
            filename, filepath, uploader_id, shareable, download_count, download_limit, 
            share_password, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id
    """
    params = (
        file['filename'],
        file['filepath'],
        file['uploader_id'],
        file['shareable'],
        file['download_count'],
        file['download_limit'],
        file['share_password'],
    )
    try:
        file_id = insert_query(query, params)
        file['id'] = file_id
    except Exception as e:
        print(f"Failed to insert untracked file {file['filename']}: {e}")
def get_request_files(req=None):
    return req.files
def get_request_file(req=None,request_file=None):
    request_files = get_request_files(req=req) or {}
    request_file = request_files.get("file")
    return request_file
def get_request_filename(req=None,request_file=None):
    request_file = request_file or get_request_file(req=req,request_file=request_file)
    request_filename = request_file.filename
    return request_filename
def get_request_safe_filename(req=None,request_file=None):
    request_filename = get_request_filename(req=req,request_file=request_file)
    if request_filename == "":
        return request_filename
    safe_filename = secure_filename(request_filename)
    return safe_filename
def get_subdir(req=None):
    subdir = req.form.get("subdir", "").strip()
    return subdir
def get_safe_subdir(req=None):
    subdir = get_subdir(req=req)
    safe_subdir = secure_filename(subdir)
    return safe_subdir
def get_user_filename(req=None):
    safe_subdir = get_safe_subdir(req=req)
    safe_filename = get_request_safe_filename(req=req)
    return filename
def get_file_id(file_dict=None, row=None):
    """
    Derive the file ID from a file dictionary or row data.
    
    Args:
        file_dict (dict, optional): Dictionary containing file data (e.g., {'id': 123, 'filename': 'example.txt'}).
        row (dict, optional): Dictionary containing row data (e.g., {'fileId': '123'}).
    
    Returns:
        int: The numeric file ID.
    
    Raises:
        ValueError: If file ID cannot be derived from file_dict or row.
    """
    if file_dict and 'id' in file_dict and file_dict['id'] is not None:
        return int(file_dict['id'])  # Numeric ID from file dictionary
    if row and 'fileId' in row and row['fileId'] is not None:
        return int(row['fileId'])  # Numeric ID from row dictionary
    raise ValueError('Unable to derive fileId: no file.id or row.fileId')
def get_user_from_path(path):
    if path.startswith(ABS_UPLOAD_ROOT):
        return path.split(ABS_UPLOAD_ROOT)[1].split('/')[0]
    return filepath.split('/')[0]
def create_file_id(filename,
                   filepath,
                   uploader_id=None,
                   shareable=False,
                   download_count=0,
                   download_limit=None,
                   share_password=False,
                   req=None,
                   *args,
                   **kwargs):
    """
    Create a new file record in the uploads table and return its file ID.
    
    Args:
        filename (str): Name of the file (e.g., 'example.txt').
        filepath (str): File path (e.g., 'user1/example.txt').
        uploader_id (str): ID of the uploader (e.g., username).
        shareable (bool, optional): Whether the file is shareable. Defaults to False.
        share_password (str, optional): Password for sharing. Defaults to None.
        download_limit (int, optional): Maximum download limit. Defaults to None.
    
    Returns:
        int: The numeric file ID (id from uploads table).
    
    Raises:
            ValueError: If the file insertion fails or no ID is returned.
        """

    filename=filename
    filepath=filepath
    uploader_id= uploader_id or get_user_name(req=req,user_name=uploader_id) or get_user_from_path(filepath)
    shareable=shareable or False
    download_count=download_count or 0
    download_limit=download_limit or None
    share_password=share_password or False
    
    query = """
        INSERT INTO uploads (
            filename, filepath, uploader_id, shareable, download_count, download_limit, share_password, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id
    """
    params = (
        filename,
        filepath,
        uploader_id,
        shareable,
        download_count,  # Initial download_count
        download_limit,
        share_password
    )
    result = select_rows(query, *params)
    if result and 'id' in result:
        return result['id']
    raise ValueError('Failed to create fileId: no ID returned from database')
