# SSHClient.py
from collections import namedtuple
import paramiko
import termios
import sys
import tty
import select
import socket
import time

class SSHClient:
    def __init__(self, username: str, password: str, address: str, port: int, ) -> None:
        self.username = username
        self.password = password
        self.address = address
        self.port = port

        self.transport = None


    def connect_ssh(self, ) -> None:
        try:
            sock = socket.create_connection((self.address, self.port), timeout=10)
            transport = paramiko.Transport((sock))
            transport.start_client()
            transport.auth_password(username=self.username, password=self.password)
            if transport.is_active():
                self.transport = transport
                return True
            else:
                transport.close()
                return False
        # except paramiko.SSHException as e:
        #     # print(f"[x] Failed to establish SSH connection: {e}")
        #     pass
        # except paramiko.AuthenticationException:
        #     # print("[x] Authentication failed, please verify your credentials")
        #     pass
        except Exception as e:
            # print(f"[x] An unexcepted error occurred: {e}")
            pass
    

    # def disconnect_ssh(self, ) -> None:
    #     self.transport.close()

    
    def invoke_shell(self, ) -> None:
        channel = self.transport.open_session()
        channel.get_pty()
        channel.invoke_shell()

        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin)
            channel.settimeout(0.0)

            while True:
                readlist, _, _ = select.select([channel, sys.stdin], [], [])
                if sys.stdin in readlist:
                    cmdline = sys.stdin.readline(1)
                    channel.sendall(cmdline)

                if channel in readlist:
                    result = channel.recv(1024)
                    if len(result) == 0:
                        print("\r\n\033[94m***** exit interactive shell *****\033[0m\r\n")
                        channel.close()
                        break
                    sys.stdout.write(result.decode('utf-8', errors='replace'))
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        channel.close()


    def execute_command(self, cmdline, ) -> str:
        channel = self.transport.open_session()
        channel.exec_command(cmdline)
        output = b""
        while True:
            chunk = channel.recv(1024)
            if not chunk:
                channel.close()
                break
            output += chunk
        channel.close()
        return output.decode() 
    

    def change_password(self, old_password, new_password) -> bool:
        channel = self.transport.open_session()
        channel.get_pty()
        channel.invoke_shell()

        time.sleep(0.5)

        while channel.recv_ready():
            output = channel.recv(1024)
        # print(1, output.decode())

        cmdline = "passwd\n"
        channel.sendall(cmdline)
        time.sleep(1.5)
        while channel.recv_ready():
            output = channel.recv(1024)
        # print(2, output.decode())
        
        if b"Authentication token manipulation error" in output or b"password unchanged" in output:
            # print(1111111111)
            return False

        if b"Current password:" in output:
            cmdline = old_password + "\n"
            channel.sendall(cmdline)
            time.sleep(1.5)
            while channel.recv_ready():
                output = channel.recv(1024)
            # print(3, output.decode())
        
        if b"Authentication token manipulation error" in output or b"password unchanged" in output:
            # print(2222222222)
            return False

        cmdline = new_password + "\n"
        channel.sendall(cmdline)
        time.sleep(1.5)
        while channel.recv_ready():
            output = channel.recv(1024)
        # print(4, output.decode())

        if b"Authentication token manipulation error" in output or b"password unchanged" in output:
            # print(3333333333)
            return False

        cmdline = new_password + "\n"
        channel.sendall(cmdline)
        time.sleep(1.5)
        while channel.recv_ready():
            output = channel.recv(1024)
        if b"password updated successfully" in output:
            return True
        elif b"Authentication token manipulation error" in output or b"password unchanged" in output:
            # print(4444444444)
            return False
        else:
            return False