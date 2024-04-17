# SSHClientManager.py
from collections import namedtuple
from SSHClient import *
import threading

SERVER_INFORMATIONS = namedtuple("server_infomations", ("username", "password", "address", "port"))

class SSHClientManager:
    def __init__(self) -> None:
        self.__lock = threading.Lock()
        self.__threads = []
        self.__sshclients = {}

    # multi-thread connection
    def establish_connection(self, server_informations):
        # connect
        def connect(username, password, address, port= 22):
            try:
                sshclient = SSHClient(username, password, address, int(port))# Create SSHClient
                ret = sshclient.connect_ssh()# Connect SSHClient
                if ret == True:
                    self.__sshclients[address] = sshclient
                else:
                    return False
            except:
                return False
        
        # multithreading
        for serverinfo in server_informations:
            thread = threading.Thread(target=connect, args=(serverinfo.username, serverinfo.password, serverinfo.address, serverinfo.port), daemon=True)
            thread.start()

    
    # single connection
    def func_single_connection(self, username, password, address, port):

        def connect(username, password, address, port= 22):
            try:
                sshclient = SSHClient(username, password, address, int(port))
                ret = sshclient.connect_ssh()# Connect SSHClient
                if ret == True:
                    self.__sshclients[address] = sshclient
                else:
                    return False
            except:
                return False
        threading.Thread(target=connect, args=(username, password, address, port, )).start()
    
    # list clients
    def list_clients(self, ):
        return self.__sshclients
    
    # execute command
    def execute_command(self, command):
        result = []
        for client_address, client_handle in self.__sshclients.items():
            result.append({client_address: client_handle.execute_command(command)})
        return result

    # interpreter
    def activate_shell(self, address):
        if address in self.__sshclients:
            self.__sshclients[address].invoke_shell()
            return True
        else:
            return False

    # change password
    def change_password(self, old_password, new_password):
        def change_pass(addr, handle, old_password, new_password):
            result = handle.change_password(old_password, new_password)
            with self.__lock:
                if result:
                    print(f"[√] {addr} password changed successfully, new password: {new_password}")
                    pass
                else:
                    print(f"\033[91m[x] {addr} password change failed, please check it!!!\033[0m")
                    pass

        for address, client_handle in self.__sshclients.items():
            thread = threading.Thread(target=change_pass, args=(address, client_handle, old_password, new_password), daemon=True)
            thread.start()
            
        for thread in self.__threads:
            thread.join()
            