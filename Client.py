import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import socket
import sys
import errno

HEADER_LENGTH = 10
IP = "10.113.18.221"
PORT = 3000

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Application")
        
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        self.entry = tk.Entry(master)
        self.entry.pack(expand=True, fill='x')

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))
        self.client_socket.setblocking(False)

        self.username = input("Username: ")
        self.send_username()

        self.master.title("Chat Application - "+self.username)

        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()

    def send_username(self):
        username = self.username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header + username) 

    def send_message(self):
        message = self.entry.get()
        if message:
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header + message)
            self.entry.delete(0, tk.END)

    def append_text(self, text, tag):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text, tag)
        self.text_area.config(state=tk.DISABLED)

    def receive_messages(self):
        while True:
            try:
                username_header = self.client_socket.recv(HEADER_LENGTH)

                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')

                message_header = self.client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')

                if username == self.username:
                    # If the message is from the sender, align to the right
                    received_message = f'{message} < You\n'
                    self.append_text(received_message, 'right_align')
                else:
                    # If the message is from others, align to the left
                    received_message = f'{username} > {message}\n'
                    self.append_text(received_message,None)

                self.text_area.see(tk.END)

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()

            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()

def main():
    root = tk.Tk()
    app = ChatApp(root)
    
    app.text_area.tag_configure('right_align', justify='right')
    
    root.mainloop()

if __name__ == "__main__":
    main()
