import tkinter as tk
import main
import threading
def start_program():
    main.running = True
    state.set("Started")
    start_button.config(text="结束", command=stop_program)
    thread = threading.Thread(target=main.main)
    thread.start()


def stop_program():
    main.running = False
    state.set("Stopped")  # 更新状态
    start_button.config(text="开始", command=start_program)

root = tk.Tk()
root.iconbitmap('yuyu.ico')
root.geometry("350x100")
root.title("HBaoi version -999")

label_author = tk.Label(root, text="老麟の赛博义手", fg="light gray")
label_author.pack(side=tk.BOTTOM, anchor="se")

state = tk.StringVar()  # 保存状态
label = tk.Label(root, textvariable=state)
label.pack()

start_button = tk.Button(root, text="开始", command=start_program)
start_button.pack()

root.mainloop()
