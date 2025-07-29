import json
import os
import time


# subcommand 1
def is_mounted(folder_path: str):
    result: bool = os.path.ismount(folder_path)
    print(f"{folder_path} is mounted: {result}")
    return result


# subcommand 2
def mount_server(username: str, server_address: str, mount_folder: str, password: str, version=None):
    """Mount nas server."""
    if version:
        mount_command = f"sudo mount -t cifs //{server_address} {mount_folder} -o username={username},password={password},vers={version}"
    else:
        mount_command = (
            f"sudo mount -t cifs //{server_address} {mount_folder} -o username={username},password={password}"
        )

    os.system(mount_command)
    return


# subcommand 3
def check_reconnect(config_file: str):
    """Check reconnects."""
    with open(config_file, "r") as file:
        config_file = json.load(file)

    for key, value in config_file.items():
        if not is_mounted(key):
            print(f"Folder {key} is not mounted. Reconnecting...")
            username = config_file.get(key).get("username")
            server_address = config_file.get(key).get("server_address")
            version = config_file.get(key).get("version")
            password = config_file.get(key).get("password")

            mount_server(username, server_address, key, password, version)

            time.sleep(5)

            if is_mounted(key):
                print(f"Successfully connected {server_address} to {key}")
            else:
                print(f"Failed to connect to {server_address}")
        else:
            print(f"Folder {key} is already mounted")

    return
