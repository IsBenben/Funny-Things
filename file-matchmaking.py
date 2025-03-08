import tkinter as tk
import os

delay = 50
score = 0

def tick():
    global score
    file_prefixes = [
        '文件',
        '消消乐',
        '游戏',
    ]
    for file_prefix in file_prefixes:
        for i in range(1, 11):
            file_name = f"{file_prefix}{i}.txt"
            content = ' '.join(file_prefix for _ in range(100)).encode('utf-8')

            try:
                if os.path.exists(file_name):
                    with open(file_name, 'rb') as f:
                        if f.read() == content:
                            continue
                with open(file_name, 'wb') as f:
                    print(f"Writing {file_name}...")
                    f.write(content)
                    score += 1
            except Exception as e:
                print(f'Errored writing {file_name}: {e}')
                pass
    label.config(text=f"Score: {score}")
    root.after(delay, tick)

root = tk.Tk()
root.title("文件消消乐")
root.attributes("-topmost", True)
root.overrideredirect(True)
root.geometry("+100+100")
root.resizable(False, False)
label = tk.Label(root, text="Score: 0", font=("Arial", 100))
label.pack(padx=30, pady=30)
root.after(delay, tick)
root.mainloop()
