import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import os

import threading
import json

# Global Variables
current_theme = "light"
counter = 0

# Theme Definitions
themes = {
    "light": {
        "bg": "#f7faff",
        "fg": "#003366",
        "entry_bg": "white",
        "entry_fg": "black",
        "button_bg": "#004080",
        "button_fg": "white",
        "log_bg": "white",
        "log_fg": "black",
        "accent": "#66ff66",
        "danger": "#ff6666"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "entry_bg": "#2a2a2a",
        "entry_fg": "#ffffff",
        "button_bg": "#3c3c3c",
        "button_fg": "#ffffff",
        "log_bg": "#121212",
        "log_fg": "#00ff88",
        "accent": "#00aa00",
        "danger": "#ff3333"
    }
}

def get_prediction(cpu, wait, conflict, priority, deadline):
    try:
        HOST = '127.0.0.1'
        PORT = 65432
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            #sock.settimeout(3) 
            sock.connect((HOST, PORT))
            data = f"{cpu},{wait},{conflict},{priority},{deadline}"
            sock.sendall(data.encode())
            result = sock.recv(1024).decode()
            return int(result)
    except Exception as e:
        return f"Error: {str(e)}"

def simulate_thread():
    global counter
    try:
        cpu = int(entry_cpu.get())
        wait = int(entry_wait.get())
        conflict = int(entry_conflict.get())
        priority = int(entry_priority.get())
        deadline = int(entry_deadline.get())

        prediction = get_prediction(cpu, wait, conflict, priority, deadline)

        if isinstance(prediction, str) and prediction.startswith("Error"):
            messagebox.showerror("Prediction Error", prediction)
            return

        theme = themes[current_theme]
        #file_path = os.path.join(os.path.dirname(__file__), "thread_input.txt")
        
        if prediction == 1:
            result_label.config(text="Thread allowed", fg=theme["accent"])
            file_path = "/mnt/c/Users/hp/Desktop/HybridML_OS_Project/thread_input.txt"
            counter += 1
            counter_label.config(text=f"Counter: {counter}")
            with open(file_path, "w") as f:
                f.write(f"{cpu} {wait} {conflict} {priority} {deadline}\n")
            log_output.insert(tk.END, f" Allowed: CPU={cpu}, Wait={wait}, Conflict={conflict}, Priority={priority}, Deadline={deadline}\n")
        elif prediction == 0:
            result_label.config(text="Thread denied", fg=theme["danger"])
            log_output.insert(tk.END, f" Denied: CPU={cpu}, Wait={wait}, Conflict={conflict}, Priority={priority}, Deadline={deadline}\n")
        else:
            result_label.config(text="Unclear prediction", fg="orange")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values.")
    

def setup_execution_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 65433))
    
    def listen():
        while True:
            data, _ = sock.recvfrom(1024)
            try:
                message = json.loads(data.decode())
                if message['type'] == 'execution':
                    log_output.insert(tk.END, 
                        f"✅ Executed: CPU={message['cpu']}, Total={message['counter']}\n")
                elif message['type'] == 'denied':
                    log_output.insert(tk.END,
                        f"❌ System Denied: CPU={message['cpu']} (Re-check failed)\n")
            except:
                pass
    
    threading.Thread(target=listen, daemon=True).start()


def clear_log():
    log_output.delete(1.0, tk.END)

def reset_fields():
    entry_cpu.delete(0, tk.END)
    entry_wait.delete(0, tk.END)
    entry_conflict.delete(0, tk.END)
    entry_priority.delete(0, tk.END)
    entry_deadline.delete(0, tk.END)

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

def apply_theme():
    theme = themes[current_theme]
    root.config(bg=theme["bg"])
    
    # Apply to all widgets
    for widget in [main_title, result_label, counter_label, log_label]:
        widget.config(bg=theme["bg"], fg=theme["fg"])
    
    # Apply to input frame and its children
    input_frame.config(bg=theme["bg"])
    for widget in input_frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Entry):
            widget.config(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
    
    # Apply to buttons
    for button in [simulate_btn, clear_btn, reset_btn, exit_btn, toggle_btn]:
        button.config(bg=theme["button_bg"], fg=theme["button_fg"])
    
    # Apply to log output
    log_output.config(bg=theme["log_bg"], fg=theme["log_fg"], insertbackground=theme["fg"])
    button_frame.config(bg=theme["bg"])

# GUI Setup
root = tk.Tk()
root.title("Hybrid ML-OS Thread Simulator (Toggle Theme)")
root.geometry("500x700")

# Main title
main_title = tk.Label(root, text="Hybrid ML-OS Simulator", font=("Segoe UI", 18, "bold"))
main_title.pack(pady=10)

# Theme toggle button
toggle_btn = tk.Button(root, text="🌙 Toggle Theme", command=toggle_theme, font=("Segoe UI", 12, "bold"))
toggle_btn.pack(pady=5)

# Input frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Input fields
tk.Label(input_frame, text="CPU Usage (0-100):", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="e", padx=10, pady=5)
entry_cpu = tk.Entry(input_frame, font=("Segoe UI", 11), width=10)
entry_cpu.grid(row=0, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Wait Time (0-10):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="e", padx=10, pady=5)
entry_wait = tk.Entry(input_frame, font=("Segoe UI", 11), width=10)
entry_wait.grid(row=1, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Past Conflicts (0-5):", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="e", padx=10, pady=5)
entry_conflict = tk.Entry(input_frame, font=("Segoe UI", 11), width=10)
entry_conflict.grid(row=2, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Priority (0-5):", font=("Segoe UI", 12)).grid(row=3, column=0, sticky="e", padx=10, pady=5)
entry_priority = tk.Entry(input_frame, font=("Segoe UI", 11), width=10)
entry_priority.grid(row=3, column=1, padx=10, pady=5)

tk.Label(input_frame, text="Deadline (0-10):", font=("Segoe UI", 12)).grid(row=4, column=0, sticky="e", padx=10, pady=5)
entry_deadline = tk.Entry(input_frame, font=("Segoe UI", 11), width=10)
entry_deadline.grid(row=4, column=1, padx=10, pady=5)

# Simulate button
simulate_btn = tk.Button(root, text="Simulate Thread", font=("Segoe UI", 12, "bold"), command=simulate_thread, padx=20, pady=10)
simulate_btn.pack(pady=10)

# Result display
result_label = tk.Label(root, text="", font=("Segoe UI", 14, "bold"))
result_label.pack(pady=5)

counter_label = tk.Label(root, text="Counter: 0", font=("Segoe UI", 14, "bold"))
counter_label.pack(pady=5)

# Log display
log_label = tk.Label(root, text="Thread Access Log", font=("Segoe UI", 14))
log_label.pack(pady=(10, 5))

log_output = scrolledtext.ScrolledText(root, height=10, font=("Consolas", 12), relief="groove", bd=2)
log_output.pack(padx=20, fill=tk.BOTH, expand=True, pady=5)

# Button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

clear_btn = tk.Button(button_frame, text="Clear Log", font=("Segoe UI", 11), command=clear_log, width=12)
clear_btn.grid(row=0, column=0, padx=5)

reset_btn = tk.Button(button_frame, text="Reset Fields", font=("Segoe UI", 11), command=reset_fields, width=12)
reset_btn.grid(row=0, column=1, padx=5)

exit_btn = tk.Button(button_frame, text="Exit", font=("Segoe UI", 11), command=root.destroy, width=12)
exit_btn.grid(row=0, column=2, padx=5)

# Apply initial theme
apply_theme()

setup_execution_listener()

root.mainloop()