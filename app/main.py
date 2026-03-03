import tkinter as tk
from tkinter import messagebox

def configurar():
    tarjeta = entry.get()
    if tarjeta:
        messagebox.showinfo("RFID", f"Tarjeta leída:\n{tarjeta}")
    else:
        messagebox.showwarning("Aviso", "Pase una tarjeta primero")

root = tk.Tk()
root.title("Sistema RFID")
root.geometry("350x200")

tk.Label(root, text="ID Tarjeta:").pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack()
entry.focus()

tk.Button(root, text="Configurar", command=configurar).pack(pady=20)

root.mainloop()