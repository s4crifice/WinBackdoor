# Remote Access Tool (RAT)

This is a Python-based Remote Access Tool (RAT) that allows for remote control of a victim's machine through a command-and-control (C2) server.

## Features

- Establishes a connection to the specified IP address and port.
- Sends and receives data reliably over the network using JSON serialization.
- Executes system commands on the victim's machine.
- Deletes files and directories.
- Reads and writes files.
- Takes screenshots of the victim's desktop.
- Dumps Wi-Fi passwords from the victim's machine.

## Usage

1. Clone the repository to your local machine.
2. Customize the IP address and port in the `Main` class constructor according to your setup.
3. Run the `main.py` script to start the RAT.
4. Connect to the C2 server from the victim's machine.

## Commands

- `exit`: Close the connection.
- `cd [directory]`: Change the working directory.
- `download [file_path]`: Download a file from the victim's machine.
- `delete [file_path]` or `delete -R [directory_path]`: Delete a file or directory.
- `wifidump`: Dump Wi-Fi passwords from the victim's machine.
- `screenshot`: Take a screenshot of the victim's desktop.
- `upload [local_file_path] [base64_encoded_content]`: Upload a file to the victim's machine.

## Disclaimer

This tool is for educational purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.

## License

This project is licensed under the MIT License.
