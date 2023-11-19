import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

class Process:
    def __init__(self, name, pid):
        self.name = name
        self.pid = pid

class ProcessManager:
    def __init__(self):
        self.processes = []

    def create_process(self, name, pid):
        new_process = Process(name, pid)
        self.processes.append(new_process)
        return new_process

    def kill_process(self, process):
        self.processes.remove(process)

    def schedule_processes(self):
        if len(self.processes) < 2:
            messagebox.showinfo("Error", "Need at least two processes for scheduling.")
        else:
            # Implement the Round Robin scheduling algorithm here
            messagebox.showinfo("Scheduling", "Round Robin scheduling not implemented yet.")

    def list_processes(self):
        if not self.processes:
            messagebox.showinfo("Processes", "No processes created yet.")
        else:
            process_list = "\n".join([f"{process.name} (PID: {process.pid})" for process in self.processes])
            messagebox.showinfo("Processes", process_list)

class ProcessManagerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Task Manager")
        self.master.geometry("400x300")
        self.master.configure(bg='#2d2d2d')  # Dark background color

        self.process_manager = ProcessManager()

        # Change the font
        custom_font = tkFont.Font(family="Helvetica", size=10)

        self.create_button = ttk.Button(master, text="Create Process", command=self.create_process, style="TButton", font=custom_font)
        self.create_button.pack(pady=10)

        self.kill_button = ttk.Button(master, text="Kill Process", command=self.kill_process, style="TButton", font=custom_font)
        self.kill_button.pack(pady=10)

        self.schedule_button = ttk.Button(master, text="Schedule Processes", command=self.schedule_processes, style="TButton", font=custom_font)
        self.schedule_button.pack(pady=10)

        self.list_button = ttk.Button(master, text="List Processes", command=self.list_processes, style="TButton", font=custom_font)
        self.list_button.pack(pady=10)

        # Style for themed Tkinter widgets
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#4d4d4d", foreground="#ffffff")
        style.configure("TButton:hover", background="#666666")

    def create_process(self):
        # You can customize this function to take input from the user, e.g., using an Entry widget.
        # For simplicity, we'll use fixed values for now.
        name = "Process " + str(len(self.process_manager.processes) + 1)
        pid = len(self.process_manager.processes) + 1
        new_process = self.process_manager.create_process(name, pid)
        messagebox.showinfo("Process Created", f"{new_process.name} created. PID: {new_process.pid}")

    def kill_process(self):
        # You can customize this function to take input from the user, e.g., using a listbox.
        # For simplicity, we'll use fixed values for now.
        if self.process_manager.processes:
            process_to_kill = self.process_manager.processes[-1]
            self.process_manager.kill_process(process_to_kill)
            messagebox.showinfo("Process Killed", f"{process_to_kill.name} killed.")
        else:
            messagebox.showinfo("Error", "No processes to kill.")

    def schedule_processes(self):
        self.process_manager.schedule_processes()

    def list_processes(self):
        self.process_manager.list_processes()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessManagerGUI(root)
    root.mainloop()
