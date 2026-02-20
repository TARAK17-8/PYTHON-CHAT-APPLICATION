import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

HOST = "127.0.0.1"
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connection error handling
try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Server is not running!")
    exit()

root = tk.Tk()
root.title("Client Chat")

chat_area = ScrolledText(root, state='disabled', width=50, height=20)
chat_area.pack(padx=10, pady=10)

entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=10)

status_label = tk.Label(root, text="Connected", fg="green")
status_label.pack()

def send_message():
    message = entry.get()
    if message:
        try:
            client.send(message.encode("utf-8"))

            chat_area.config(state='normal')
            chat_area.insert(tk.END, "Client: " + message + "\n")
            chat_area.config(state='disabled')
            entry.delete(0, tk.END)

            # BYE condition
            if message.lower() == "bye":
                disconnect()

        except OSError:
            messagebox.showerror("Error", "Connection closed.")

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")

            if not message:
                break

            # BYE condition from server
            if message.lower() == "bye":
                chat_area.config(state='normal')
                chat_area.insert(tk.END, "Server ended the chat.\n")
                chat_area.config(state='disabled')
                break

            chat_area.config(state='normal')
            chat_area.insert(tk.END, "Server: " + message + "\n")
            chat_area.config(state='disabled')

        except ConnectionResetError:
            break
        except OSError:
            break

    disconnect()

def disconnect():
    try:
        client.close()
    except OSError:
        pass

    status_label.config(text="Disconnected", fg="red")
    root.quit()

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.LEFT, padx=5)

disconnect_button = tk.Button(root, text="Disconnect", command=disconnect)
disconnect_button.pack(side=tk.LEFT, padx=5)

thread = threading.Thread(target=receive_messages)
thread.daemon = True
thread.start()

root.protocol("WM_DELETE_WINDOW", disconnect)

root.mainloop()