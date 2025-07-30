import logging
import os
import shutil
import glob
from datetime import datetime

logger = logging.getLogger('root')


def backup_possible(connection_string: str, backup_path: str) -> bool:
    if not connection_string or not backup_path:
        logger.error(f"Could not restore because one or more parameters are None. backup_path:'{backup_path}' "
                     f"connection_string:'{connection_string}'")
        return False

    # Prüfen, ob Datenbank für Backup unterstützt wird
    if not is_db_supported(connection_string):
        logger.error(f"Backup of cache db failed: Database has to be file based and abslute path.")
        return False

    # Prüfen, ob die DB-Datei mit absolutem Pfad vorliegt
    abs_db_file = get_abs_db_file_name(connection_string)
    if not abs_db_file:
        logger.error(f"Backup not possible: Could not get absolute file path")
        return False

    return True


def is_db_supported(connection_string: str) -> bool:
    supported_prefixes = ["sqlite:////"]
    return any(supported_prefix in connection_string.lower() for supported_prefix in supported_prefixes)


def get_abs_db_file_name(connection_string: str) -> str | None:
    try:
        abs_db_file = connection_string.split("///")[1]
    except IndexError:
        return None
    return abs_db_file


def restore_last_backup(backup_path: str, connection_string: str) -> bool:
    if not backup_possible(connection_string, backup_path):
        return False

    abs_db_file = get_abs_db_file_name(connection_string)
    if not abs_db_file:
        logger.error(f"Could not get absolute db file path from '{connection_string}'")
        return False

    files = glob.glob(os.path.join(backup_path, "*"))
    files_with_time = [(file, os.path.getmtime(file)) for file in files if os.path.isfile(file)]

    if files_with_time:
        newest_file = max(files_with_time, key=lambda x: x[1])[0]

        try:
            shutil.copy(newest_file, abs_db_file)
            logger.warning(f"Backup '{os.path.basename(newest_file)}' has been copied to '{abs_db_file}'.")
        except Exception as e:
            logger.error(f"Error copying the file: {e}")
            return False
    else:
        print("No files found in the source folder.")
        return False
    return True


def cleanup_backups(backup_path: str):
    files = glob.glob(os.path.join(backup_path, "*"))

    files_with_time = [(tfile, os.path.getmtime(tfile)) for tfile in files if os.path.isfile(tfile)]
    sorted_files = sorted(files_with_time, key=lambda x: x[1],
                          reverse=True)

    files_to_delete = sorted_files[7:]

    for tfile, _ in files_to_delete:
        try:
            os.remove(tfile)
        except Exception as e:
            print(f"Error while deletion of {tfile}: {e}")


def backup_database(connection_string: str, backup_path: str) -> bool:
    if not backup_possible(connection_string, backup_path):
        return False

    abs_db_file = get_abs_db_file_name(connection_string)
    if not abs_db_file:
        logger.error(f"Could not get absolute db file path from '{connection_string}'")
        return False

    # Aktuelle DB-Datei in Backup-Path kopieren
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_name = f"{stamp}_{os.path.basename(abs_db_file)}"
    abs_backup_path = os.path.join(backup_path, backup_file_name)

    try:
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        shutil.copy(abs_db_file, abs_backup_path)
        logger.info(f"Backup of cache database successful! Destination file: {abs_backup_path}")

    except FileNotFoundError:
        logger.error(f"Backup of cache database failed: File {abs_db_file} not found!")
        return False
    except PermissionError:
        logger.error(f"Backup of cache database failed for file {abs_backup_path}: Permission error")
        return False
    except Exception as e:
        logger.error(f"Backup of cache database failed. Unexpected error: {str(e)}")
        return False

    cleanup_backups(backup_path)

    return True
