import paramiko
import time
import subprocess
import telnetlib

file_path = 'config_commands.txt'

# Initialize counter variable
telnet_success_counter = 0

def configFile(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the entire contents of the file
            file_contents = file.read()
        return file_contents  # Return the file contents
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except PermissionError:
        print(f"Permission error. Make sure you have the necessary permissions to read the file.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function with the file path and store the result
file_contents = configFile(file_path)

def ssh_connect(hostname, username, password, enable_password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password, look_for_keys=False, allow_agent=False)

    # Open an interactive shell
    shell = client.invoke_shell()

    # Wait for the shell to be ready
    time.sleep(2)

    # Send the enable command and password
    shell.send("enable\n")
    time.sleep(1)
    shell.send(f"{enable_password}\n")
    time.sleep(1)

    # Clear the initial switch prompts
    shell.recv(65535)

    return client, shell

def disable_all_ports(ssh_shell):
    commands = [
        "conf t\n",
        "int range Gi3/0/2 - 48\n",
        "shutdown\n",
        "exit\n",
    ]
    for command in commands:
        ssh_shell.send(command)
        time.sleep(2)  # Add a delay to ensure each command is processed

def enable_and_test_ports(ssh_shell, file_contents):
    global telnet_success_counter  # Declare the counter variable as global

    for port in range(2, 49):
        enable_command = f"conf t\nint gig3/0/{port}\nno shutdown\nend\n"
        ssh_shell.send(enable_command)
        time.sleep(2)  # Add a delay to ensure each command is processed

        # Add a delay before initiating the telnet connection
        time.sleep(35)  # Adjust the delay duration based on your needs

        # Test telnet and ping using telnetlib
        try:
            tn = telnetlib.Telnet("192.168.2.1")
            tn.read_until(b"Router login:")
            tn.write(b"adm\n")
            tn.read_until(b"Password:")
            tn.write(b"123456\n")
            print("Login Successful")
            tn.read_until(b"Router>")  # Change to bytes literal
            tn.write(b"enable\n")
            tn.read_until(b"input password:")
            tn.write(b"123456\n")
            tn.read_until(b"Router#")
            tn.write(b"conf terminal\n")
            tn.read_until(b"Router(config)#")
            tn.write(b"config import\n")
            tn.read_until(b"Paste system config")
            for line in file_contents.split('\n'):
                if line:
                    tn.write(line.encode('utf-8') + b'\n')
                    print(f"Sent command: {line}")  # Add this line to print the sent command
            print(file_contents)
            time.sleep(1)
            tn.write(b"y\n")
            tn.read_until(b"Import config file successfully!")
            print("Import config file successfully!")
            tn.close()
            print(f"Port Gi3/0/{port} - Telnet Success")

            # Increment the counter on successful Telnet
            telnet_success_counter += 1
        except Exception as e:
            print(f"Port Gi3/0/{port} - Telnet Failed: {e}")

        # Disable the current port
        disable_command = f"conf t\nint gig3/0/{port}\nshutdown\nend\n"
        ssh_shell.send(disable_command)
        time.sleep(2)  # Add a delay to ensure each command is processed

def main():
    # Replace these values with your Cisco switch details
    switch_hostname = "192.168.2.254"
    switch_username = "CRI"
    switch_password = "CRI"
    enable_password = "CRI"

    # Connect to the Cisco switch
    ssh_client, shell = ssh_connect(switch_hostname, switch_username, switch_password, enable_password)

    if ssh_client and shell:
        # Disable all ports except Gi3/0/1
        disable_all_ports(shell)

        # Enable and test ports one by one
        enable_and_test_ports(shell, file_contents)

        # Close the SSH connection
        shell.close()
        ssh_client.close()

        print(f"Telnet Success Count: {telnet_success_counter}")

if __name__ == "__main__":
    main()