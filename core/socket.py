import socket


class INRDBSocket:
    """ Generic socket wrapper to perform INRDB bulk queries """

    def __init__(self,host,port):

        self.buffer = ''
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((self.host, self.port))
        except socket.error as error_msg:
            self.close_socket(
                f"Could not initialize the socket {self.host}:{self.port} - {error_msg}"
            )

        self.send_line("-k")
        ack = self.receive_line()
        if ack != "% This is RIPE NCC's Routing Information Service":
            self.close_socket(f"Connection handshake failed. Received: {ack}")
        else:
            last_line = ack
            current_line = self.receive_line()

            while last_line != '' and current_line != '':
                last_line = current_line
                current_line = self.receive_line()

    def send_line(self, msg):

        current_line = msg + '\n'
        total_sent = 0
        while total_sent < len(current_line):
            sent = self.sock.send(current_line[total_sent:].encode('utf-8'))
            if sent == 0:
                self.close_socket(f"Socket connection broken: {self.host}:{self.port}")
            total_sent = total_sent + sent

    def receive_line(self):

        index = self.buffer.find("\n")
        if index == -1:
            # No new line, but potentially still some bytes in buffer
            # We still have data from previous call
            current_line = self.buffer
            new_line = False
        else:
            current_line = ''
            chunk = self.buffer
            new_line = True
    
        while not new_line:
            chunk = self.sock.recv(8192).decode("utf-8")

            if chunk == '':
                self.close_socket(f"Socket connection broken: {self.host}:{self.port}")
            index = chunk.find("\n")
            if index == -1:
                current_line += chunk
            else:
                new_line = True
    
        current_line += chunk[0:index]
        self.buffer = chunk[index+1:len(chunk)]

        return current_line

    def close_socket(self, raise_exception_with_msg=""):

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

        if raise_exception_with_msg:
            raise RuntimeError(raise_exception_with_msg)