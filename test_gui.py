import tkinter as tk

root = tk.Tk()
root.title("GUI Test")
root.geometry("500x400")

tk.Label(
    root,
    text="TKINTER IS WORKING!",
    font=("Arial", 20, "bold")
).pack(pady=50)

tk.Entry(root).pack(pady=20)

tk.Button(
    root,
    text="SEND",
    font=("Arial", 14)
).pack()

root.mainloop()