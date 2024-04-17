"""
Data: 04/17/2024
Author: Melancholy666
Comment: 写的什么钩十代码xD
"""

# main.py
from SSHClientManager import *
from SSHClient import *
import threading
import readline
import argparse

lock = threading.Lock()
server_informations = []


class RequirePasswordAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if hasattr(namespace, "username") and not hasattr(namespace, "password"):
            parser.error("When specifying a username, a password must also be provided")
        setattr(namespace, self.dest, values)
def parse_arguments():
    parser = argparse.ArgumentParser(description="SSH Client")
    parser.add_argument("--ip_files", required=True, help="SSH server host address")
    # parser.add_argument("--port", type=int, default=22, help="SSH server port (default: 22)")
    # parser.add_argument("--username", help="SSH username")
    # parser.add_argument("--password", action=RequirePasswordAction, help="SSH password")
    # parser.add_argument("--timeout", type=int, default=10, help="Connection timeout in seconds (default: 10)")
    return parser.parse_args()

def complete(text, state):
    options = {
        "help": [],
        "sessions": ["connect", "list", "activate", "execute", "changepass"],
        "exit": [],
        "quit": []
    }
    buffer = readline.get_line_buffer().split(" ")
    if len(buffer) <= 1:
        return [cmd+" " for cmd in options.keys() if cmd.startswith(text)][state]
    elif len(buffer) == 2:
        return [cmd + " " for cmd in options[buffer[0]] if cmd.startswith(text)][state]
    else:
        return None

def main(ip_list, username=None, password=None, port=22):
    with open(ip_list, "r") as f:
        serverinfo = f.readlines()
        for i in range(len(serverinfo)):
            info = serverinfo[i].split()
            if not username or not password:
                try:
                    server_informations.append(SERVER_INFORMATIONS(address=info[0], username=info[1], password=info[2], port=info[3]))
                except Exception as e:
                    pass
            else:
                try:
                    server_informations.append(SERVER_INFORMATIONS(address=info[0], username=username, password=password, port=port))
                except Exception as e:
                    pass

    sshclientmanager = SSHClientManager()
    sshclientmanager.establish_connection(server_informations)

    print("\033[94mWelcome to SSH Interpreter\033[0m")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)

    while True:
        cmdline = input("\033[95mIn SSH>\033[0m")
        operation = " ".join(cmdline.split()[:2])
        command = " ".join(cmdline.split()[2:])
        
        if cmdline == "exit" or cmdline == "quit":
            print("\033[94mBye!\033[0m")
            break
        
        elif cmdline == "help":
            print("\033[91mhelp\033[0m: show this help")
            print()
            print("\033[91mexit\033[0m: exit the program")
            print()
            print("\033[93msessions\033[0m:")
            print("\t\033[91msessions list\033[0m: list all sessions")
            print("\t\033[91msessions connect\033[0m \033[94m<address> <username> <password> <port>\033[0m: connect to a server")
            # print("sessions disconnect <address>: disconnect from a server")
            print("\t\033[91msessions execute\033[0m \033[94m<command>\033[0m: execute a command on all servers")
            print("\t\033[91msessions activate\033[0m \033[94m<address>\033[0m: activate a shell on a server")
            print("\t\033[91msessions changepass\033[0m \033[94m<old password> <new password>\033[0m: change password on all server")
            print()
        elif operation == "sessions connect":
            if len(command.split()) == 4:
                address, username, password, port = command.split()
                sshclientmanager.func_single_connection(username, password, address, port)
            else:
                print("\033[93mUsage\033[0m: \033[91msessions connect\033[0m \033[94m<address> <username> <password> <port>\033[0m")

        elif operation == "sessions execute":
            result = sshclientmanager.execute_command(command)
            for clients_info in result:
                for address, result in clients_info.items():
                    print(f"\033[94m----------\033[0m\033[91m{address}\033[0m\033[94m----------\033[0m")
                    print(f"{result}")

        elif operation == "sessions list":
            result = sshclientmanager.list_clients()
            print(f"\033[94m##########\033[0m \033[93m{operation}\033[0m \033[94m##########\033[0m")
            if result == {}:
                print("no session!")
            else:
                for address, client_handle in result.items():
                    print(f"\033[92m{client_handle.username}\033[0m@\033[91m{address}\033[0m:\033[94m{client_handle.port}\033[0m => \033[93m{client_handle}\033[0m")
                print()
        elif operation == "sessions activate":
            if len(command.split()) == 1:
                result = sshclientmanager.activate_shell(command)
                if result == False:
                    print("\033[91m[x] activate session failed\033[0m")
            else:
                print("\033[93mUsage\033[0m: \033[91msessions activate\033[0m \033[94m<address>\033[0m")
        
        elif operation == "sessions changepass":
            if len(command.split()) == 2:
                old_pass, new_pass = command.split()
                result = sshclientmanager.change_password(old_pass, new_pass)
                if result == False:
                    print("\033[91m[x] change password failed\033[0m")
            else:
                print("\033[93mUsage\033[0m: \033[91msessions changepass\033[0m \033[94m<old password> <new password>\033[0m")


if __name__ == "__main__":
    # ip_list = "ip.txt"
    # username = "kali"
    # password = "kali"
    # port = 22
    
    args = parse_arguments()
    main(args.ip_files)
    