import tkinter.ttk as ttk
import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class ServerWindow(ttk.Frame):
    def __init__(self, root, **kw):
        super().__init__(**kw)
        self.root = root

        self.__set_layout()
        self.__insert_msg(self.text_log, '[LOG] Setup server...\n', 'log')
        self.__setup_server()
        self.__insert_msg(self.text_log, '[LOG] Waiting for connections...\n', 'log')

    def __del__(self):
        self.SERVER.close()
        print(self.clients)
        print(self.addresses)
        print(self.open_ports)

    def __setup_server(self):
        self.clients = {}
        self.addresses = {}
        self.open_ports = [5000]

        HOST = '127.0.0.1'
        PORT = 5000
        self.BUFFER_SIZE = 1024

        ADDRESS = (HOST, PORT)
        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.SERVER.bind(ADDRESS)

        self.SERVER.listen(20)

        self.accept_thread = Thread(target = self.__accept_incoming_connections)
        self.accept_thread.start()

        print(self.SERVER.getsockname())

    def __accept_incoming_connections(self):
        while True:
            client, client_address = self.SERVER.accept()
            client.send('[USER] Greetings from the ChatRoom!\n'.encode('utf8'))
            self.addresses[client] = client_address
            Thread(target = self.__handle_client, args = (client, client_address)).start()

    def __handle_client(self, client, client_address):
        name = client.recv(self.BUFFER_SIZE).decode('utf8')
        welcome = f'[USER] Welcome {name}!\n'
        client.send(welcome.encode('utf8'))

        msg = f'[UPDATE] {name} joined!\n'
        self.__broadcast(msg.encode('utf8'))

        self.__insert_msg(self.text_log, f'[UPDATE] {name}({":".join(list(map(str, self.addresses[client])))}) '
                                         f'has connected!\n', 'update')
        self.clients[client] = name
        self.__update_users()

        while True:
            msg = client.recv(self.BUFFER_SIZE)
            if msg != '#quit'.encode('utf8'):
                self.__broadcast(msg, name + ': ')
                self.__insert_msg(self.text_log, f'[LOG] {name}({":".join(list(map(str, self.addresses[client])))}):'
                                                 f' {msg.decode("utf8")}\n', 'log')
            else:
                client.send(f'{name}: #quit'.encode('utf8'))
                client.close()
                del self.clients[client]

                self.__broadcast(f'[UPDATE] {name} has left!\n'.encode('utf8'))
                self.__insert_msg(self.text_log, f'[UPDATE] {name}({":".join(list(map(str, self.addresses[client])))}) '
                                                 f'has disconnected!\n', 'update')

                del self.addresses[client]
                self.__update_users()
                break

    def __broadcast(self, msg, prefix = ''):
        for sock in self.clients:
            sock.send(prefix.encode('utf8') + msg)

    def __set_layout(self):
        self.root.title('Server')
        self.root.iconphoto(False, tk.PhotoImage(file = '..\\chat.png'))

        self.root.minsize(550, 290)
        self.root.maxsize(725, 290)

        self.frame_data = ttk.Frame(self.root)
        self.frame_data.pack(fill = tk.BOTH)
        self.frame_data.columnconfigure(2, weight = 2)

        self.label_port = ttk.Label(self.frame_data, text = 'Local port:')
        self.label_port.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = tk.W)

        self.entry_port = ttk.Entry(self.frame_data)
        self.entry_port.grid(row = 1, column = 2, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_port = ttk.Button(self.frame_data, text = 'Open port',
                                      command = lambda: self.__open_port(self.entry_port.get()))
        self.button_port.grid(row = 1, column = 3, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.button_clear = ttk.Button(self.frame_data, text = 'Clear log')
        self.button_clear.grid(row = 1, column = 4, padx = 5, pady = 5, sticky = tk.W + tk.E)

        self.frame_log = ttk.Frame(self.frame_data)
        self.frame_log.grid(row = 2, column = 1, columnspan = 3, padx = 5, pady = 5)

        scrollbar_log = ttk.Scrollbar(self.frame_log)
        scrollbar_log.pack(side = tk.RIGHT, fill = tk.BOTH)

        self.text_log = tk.Text(self.frame_log, height = 16, state = tk.DISABLED,
                                font = 'Consolas 10', yscrollcommand = scrollbar_log.set)
        self.text_log.pack(side = tk.LEFT, fill = tk.BOTH)

        self.frame_users = ttk.Frame(self.frame_data)
        self.frame_users.grid(row = 2, column = 4, padx = 5, pady = 5)

        scrollbar_users = ttk.Scrollbar(self.frame_users)
        scrollbar_users.pack(side = tk.RIGHT, fill = tk.Y)

        self.text_users = tk.Text(self.frame_users, height = 18, width = 24, state = tk.DISABLED,
                                  font = 'Consolas 8', yscrollcommand = scrollbar_users.set)
        self.text_users.pack(side = tk.LEFT, fill = tk.BOTH)

        self.button_clear.configure(command = lambda: self.__clear_text(self.text_log))

        self.text_log.tag_config('error', foreground = 'red')
        self.text_log.tag_config('warning', foreground = 'blue')
        self.text_log.tag_config('log', foreground = 'black')
        self.text_log.tag_config('exception', foreground = 'purple')
        self.text_log.tag_config('update', foreground = 'green')

    def __insert_msg(self, textbox, text, tag):
        textbox.configure(state = tk.NORMAL)
        textbox.insert(tk.END, text, tag)
        textbox.configure(state = tk.DISABLED)

    def __clear_text(self, textbox):
        textbox.configure(state = tk.NORMAL)
        textbox.delete('1.0', tk.END)
        textbox.configure(state = tk.DISABLED)

    def __open_port(self, port):
        try:
            if port == '':
                self.__insert_msg(self.text_log, '[ERROR] Empty entry for local port opening!\n', 'error')
            elif len(port) > 5 or port == '0' or 1 > int(port) > 49151:
                self.__insert_msg(self.text_log, f'[ERROR] Invalid port number!\n', 'error')
            elif int(port) in self.open_ports:
                self.__insert_msg(self.text_log, f'[ERROR] Port: {port} already has been opened!\n', 'error')
            else:
                self.open_ports.append(int(port))
                self.__insert_msg(self.text_log, f'[UPDATE] Port: {port} has been opened!\n', 'update')
        except Exception as e:
            self.__insert_msg(self.text_log, f'[EXCEPTION] Raised exception: {e}\n', 'exception')

    def __update_users(self):
        self.__clear_text(self.text_users)
        for client in self.clients.keys():
            name = self.clients[client]
            host, port = self.addresses[client]
            self.__insert_msg(self.text_users, f'{name}({host}:{port})\n', 'log')


if __name__ == '__main__':
    app = ServerWindow(tk.Tk())
    app.root.mainloop()
