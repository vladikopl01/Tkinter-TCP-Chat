import tkinter.ttk as ttk
import tkinter as tk
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from time import sleep


class ClientWindow(ttk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.root = root
        self.__set_layout()

    def __del__(self):
        pass

    def __set_client(self):
        try:
            HOST = self.entry_host.get()
            PORT = self.entry_port.get()

            if not PORT and not HOST:
                self.__insert_msg(self.text_chat, '[ERROR] Empty entry for host and port input!\n', 'error')
            elif not PORT:
                self.__insert_msg(self.text_chat, '[ERROR] Empty entry for port input!\n', 'error')
            elif not HOST:
                self.__insert_msg(self.text_chat, '[ERROR] Empty entry for host input!\n', 'error')
            else:
                self.__insert_msg(self.text_chat, '[LOG] Try to connect...\n', 'log')
                self.ADDRESS = (HOST, int(PORT))
                self.BUFFER_SIZE = 1024
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.client_socket.connect(self.ADDRESS)

                self.receive_thread = Thread(target = self.__receive)
                self.receive_thread.start()

                self.client_msg.set(self.entry_name.get())
                self.__send()
        except Exception as e:
            self.__insert_msg(self.text_chat, f'[EXCEPTION] Raised exception: {e}\n', 'exception')

    def __receive(self):
        while True:
            try:
                msg = self.client_socket.recv(self.BUFFER_SIZE).decode('utf8')
                if 'ERROR' in msg:
                    self.__insert_msg(self.text_chat, msg, 'error')
                elif 'USER' in msg:
                    self.__insert_msg(self.text_chat, msg, 'user')
                elif 'UPDATE' in msg:
                    self.__insert_msg(self.text_chat, msg, 'update')
                else:
                    self.__insert_msg(self.text_chat, msg + '\n')
            except:
                break

    def __send(self, event = None):
        try:
            msg = self.client_msg.get()
            self.client_msg.set('')
            self.client_socket.send(bytes(msg, 'utf8'))
            if msg == '#quit':
                sleep(2)
                self.client_socket.close()

        except (OSError, AttributeError) as e:
            self.__insert_msg(self.text_chat, f'[ERROR] Firstly, connect to chat room!\n', 'error')
        except Exception as e:
            self.__insert_msg(self.text_chat, f'[EXCEPTION] Raised exception: {e}\n', 'exception')

    def __on_closing(self):
        try:
            self.client_msg.set('#quit')
            self.__send()
            self.quit()
        except Exception as e:
            self.__insert_msg(self.text_chat, f'[EXCEPTION] Raised exception: {e}\n', 'exception')

    def __disconnect(self):
        self.client_msg.set('#quit')
        self.__send()

    def __set_layout(self):
        self.root.title('Client')
        self.root.iconphoto(False, tk.PhotoImage(file = '..\\chat.png'))

        self.root.minsize(700, 325)
        self.root.maxsize(830, 325)

        self.frame_data = ttk.Frame(self.root)
        self.frame_data.pack(fill = tk.BOTH)
        self.frame_data.columnconfigure(2, weight = 2)
        self.frame_data.columnconfigure(4, weight = 2)
        self.frame_data.columnconfigure(6, weight = 2)

        self.label_host = ttk.Label(self.frame_data, text = 'Host:')
        self.label_host.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)
        self.entry_host = ttk.Entry(self.frame_data)
        self.entry_host.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.label_port = ttk.Label(self.frame_data, text = 'Port:')
        self.label_port.grid(row = 1, column = 3, padx = 5, pady = 5, sticky = tk.W)
        self.entry_port = ttk.Entry(self.frame_data)
        self.entry_port.grid(row = 1, column = 4, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.label_name = ttk.Label(self.frame_data, text = 'Name:')
        self.label_name.grid(row = 1, column = 5, padx = 5, pady = 5, sticky = tk.W)
        self.entry_name = ttk.Entry(self.frame_data)
        self.entry_name.grid(row = 1, column = 6, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_connect = ttk.Button(self.frame_data, text = 'Connect')
        self.button_connect.grid(row = 1, column = 7, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_disconnect = ttk.Button(self.frame_data, text = 'Disconnect')
        self.button_disconnect.grid(row = 1, column = 8, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.label_msg = ttk.Label(self.frame_data, text = 'Message:')
        self.label_msg.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = tk.W)
        self.entry_msg = ttk.Entry(self.frame_data)
        self.entry_msg.grid(row = 2, column = 2, columnspan = 5, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_send = ttk.Button(self.frame_data, text = 'Send')
        self.button_send.grid(row = 2, column = 7, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_clear = ttk.Button(self.frame_data, text = 'Clear chat')
        self.button_clear.grid(row = 2, column = 8, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.frame_chat = ttk.Frame(self.frame_data)
        self.frame_chat.grid(row = 3, column = 1, columnspan = 8, padx = 5, pady = 5)

        scrollbar_chat = ttk.Scrollbar(self.frame_chat)
        scrollbar_chat.pack(side = tk.RIGHT, fill = tk.BOTH)

        self.text_chat = tk.Text(self.frame_chat, height = 16, width = 256, state = tk.DISABLED,
                                 font = 'Consolas 10', yscrollcommand = scrollbar_chat.set)
        self.text_chat.pack(side = tk.LEFT, fill = tk.BOTH)

        self.root.protocol('WM_DELETE_WINDOW', self.__on_closing)

        self.client_msg = tk.StringVar()
        self.entry_msg.configure(textvariable = self.client_msg)
        self.entry_msg.bind('<Return>', self.__send)

        self.button_connect.configure(command = self.__set_client)
        self.button_disconnect.configure(command = self.__disconnect)
        self.button_send.configure(command = self.__send)
        self.button_clear.configure(command = self.__clear_text)

        self.text_chat.tag_config('msg', foreground = 'black')
        self.text_chat.tag_config('user', foreground = 'blue')
        self.text_chat.tag_config('update', foreground = 'green')
        self.text_chat.tag_config('error', foreground = 'red')
        self.text_chat.tag_config('exception', foreground = 'purple')

    def __insert_msg(self, textbox: tk.Text, text, tag = 'msg'):
        textbox.configure(state = tk.NORMAL)
        textbox.insert(tk.END, text, tag)
        textbox.configure(state = tk.DISABLED)

    def __clear_text(self):
        self.text_chat.configure(state = tk.NORMAL)
        self.text_chat.delete('1.0', tk.END)
        self.text_chat.configure(state = tk.DISABLED)


if __name__ == '__main__':
    app = ClientWindow(tk.Tk())
    app.root.mainloop()
