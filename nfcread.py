# nfcread.py
# Uses nfcpy to drive an NFC tag reader to continuously scan for 
# supported tags. Commands can be executed based on tag IDs.

# This file is in the public domain (Unlicense). https://unlicense.org

import tomllib
import subprocess
import time

import nfc

def main():
    try:
        with open("nfcread.toml","rb") as nfc_toml_file:
            nfc_toml = tomllib.load(nfc_toml_file)
    except IOError:
        print("nfcread.toml not found.")
        exit(1)
    except tomllib.TOMLDecodeError:
        print("Error reading nfcread.toml.")
        exit(1)
        
    COM_PORT = str(nfc_toml['reader']['com_port'])
    DRIVER = nfc_toml['reader']['driver']
    REMOVE_TIMEOUT = nfc_toml['reader']['remove_timeout']

    tag_commands = nfc_toml['tag_commands']

    remove_timeout = 0
    current_tag = None
    command = None
    old_command = None

    clf = nfc.ContactlessFrontend()
    if clf.open(f"com:{COM_PORT}:{DRIVER}"):
        print(f"{DRIVER} NFC reader on COM{COM_PORT} opened.")
    else:
        print("No card reader connected.")
        exit(1)

    try:
        while True:
            target = clf.sense(nfc.clf.RemoteTarget("106A"), iterations=1)
            if target:
                if hasattr(target, "sdd_res"):
                    print(f"Tag scanned. ID: {target.sdd_res.hex()}")
                    tag_id = target.sdd_res.hex()

                    # If a tag was removed and a different tag is read
                    # before the remove timeout, execute the exit action
                    # immediately before executing the new command.
                    # Wait 1 second after the exit action completes before
                    # continuing to ensure cleanup has completed.
                    if current_tag is not None and current_tag != tag_id:
                        print("Executing exit action before new command.")
                        exit_action = subprocess.Popen("exit.bat", shell=True)
                        while True:
                            try:
                                exit_action.wait(timeout=3)
                                break
                            except TimeoutError:
                                print("Exit action timed out. Retrying.")
                                continue
                        time.sleep(1)
                    current_tag = tag_id
                    command = tag_commands.get(tag_id)
                    if command is not None and old_command != command:
                        remove_timeout = REMOVE_TIMEOUT
                        print(f"Executing command: {command}")
                        old_command = command
                        subprocess.Popen(command, shell=True)
                    elif old_command == command and old_command is not None:
                        print("Prior tag scanned. Cancelling exit action.")
                        remove_timeout = REMOVE_TIMEOUT
                    else:
                        print("No command defined for this tag.")
                        remove_timeout = 0
                else:
                    print("Unsupported tag scanned.")

                # Idle while tag is present.
                while clf.sense(nfc.clf.RemoteTarget("106A"), iterations=1):
                    pass
            else:
                if current_tag is not None:
                    if command is not None:
                        if remove_timeout == REMOVE_TIMEOUT:
                            print(f"Tag removed. Waiting {REMOVE_TIMEOUT} seconds before executing exit action.")
                        if remove_timeout > 0:
                            print(f"Remaining time: {remove_timeout}")
                            remove_timeout -= 1
                            time.sleep(1)
                        else:
                            exit_action = subprocess.Popen("exit.bat", shell=True)
                            while True:
                                try:
                                    exit_action.wait(timeout=3)
                                    break
                                except TimeoutError:
                                    print("Exit action timed out. Retrying.")
                                    continue
                            current_tag = None
                            command = None
                            old_command = None
                    else:
                        print("Tag removed.")
                        current_tag = None
                        command = None
                        old_command = None

    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        clf.close()


if __name__ == "__main__":
    main()
