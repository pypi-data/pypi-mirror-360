import os
from ws_bom_robot_app.config import config
from datetime import datetime, timedelta
from ws_bom_robot_app.util import _log

def kb_cleanup_data_file() -> dict:
    """
    clean up old data files in the specified folder

    Returns:
    - Dictionary with cleanup statistics
    """
    _deleted_files = []
    _freed_space = 0
    folder = os.path.join(config.robot_data_folder, config.robot_data_db_folder, config.robot_data_db_folder_out)

    for root, dirs, files in os.walk(folder, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            file_stat = os.stat(file_path)
            file_creation_time = datetime.fromtimestamp(file_stat.st_ctime)
            if file_creation_time < datetime.now() - timedelta(days=config.robot_data_db_retention_days):
                _freed_space += file_stat.st_size
                os.remove(file_path)
                _deleted_files.append(file_path)
        if not os.listdir(root):
            os.rmdir(root)

    _log.info(f"Deleted {len(_deleted_files)} files; Freed space: {_freed_space / (1024 * 1024):.2f} MB")

    return {
        "deleted_files_count": len(_deleted_files),
        "freed_space_mb": _freed_space / (1024 * 1024)
    }
