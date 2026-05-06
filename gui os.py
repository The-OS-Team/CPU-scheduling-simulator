import copy
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np

# =========================
# SCHEDULING ALGORITHMS
# =========================

def sjf(processes):
    if not processes: return []
    procs = sorted([p[:] for p in processes], key=lambda p: (p[1], p[0]))
    ready = []
    schedule = []
    time = 0
    completed = 0
    n = len(procs)
    i = 0
    while completed < n:
        while i < n and procs[i][1] <= time:
            ready.append(procs[i])
            i += 1
        if ready:
            ready.sort(key=lambda p: (p[2], p[0]))
            pid, arrival, burst = ready.pop(0)
            start = time
            time += burst
            schedule.append((pid, start, time))
            completed += 1
        else:
            if i < n: time = procs[i][1]
            else: break
    return schedule

def srtf(processes):
    if not processes: return []
    procs = sorted([p[:] for p in processes], key=lambda p: p[1])
    remaining_time = {p[0]: p[2] for p in procs}
    n = len(procs)
    schedule = []
    current_time = 0
    completed = 0
    last_pid = None
    segment_start = 0

    while completed < n:
        available = [p for p in procs if p[1] <= current_time and remaining_time[p[0]] > 0]
        if not available:
            if last_pid is not None:
                schedule.append((last_pid, segment_start, current_time))
                last_pid = None
            next_arrival = min([p[1] for p in procs if p[1] > current_time], default=current_time + 1)
            current_time = next_arrival
            continue

        best_p = min(available, key=lambda p: (remaining_time[p[0]], p[0]))
        pid = best_p[0]

        if pid != last_pid:
            if last_pid is not None:
                schedule.append((last_pid, segment_start, current_time))
            last_pid = pid
            segment_start = current_time

        remaining_time[pid] = round(remaining_time[pid] - 0.1, 2)
        current_time = round(current_time + 0.1, 2)

        if remaining_time[pid] <= 0:
            schedule.append((pid, segment_start, current_time))
            completed += 1
            last_pid = None

    refined = []
    if schedule:
        cp, cs, ce = schedule[0]
        for i in range(1, len(schedule)):
            p, s, e = schedule[i]
            if p == cp: ce = e
            else:
                refined.append((cp, cs, ce))
                cp, cs, ce = p, s, e
        refined.append((cp, cs, ce))
    return refined

# =========================
# GUI APP
# =========================

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Project: SJF vs SRTF Analysis")
        self.root.geometry("950x700")
        
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Shortest Job First (SJF) & SRTF Scheduler", font=("Arial", 14, "bold")).pack(pady=5)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text=" Add New Process ", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        labels = ["PID:", "Arrival:", "Burst:"]
        self.entries = []
        for i, text in enumerate(labels):
            ttk.Label(input_frame, text=text).grid(row=0, column=i*2, padx=5)
            entry = ttk.Entry(input_frame, width=10)
            entry.grid(row=0, column=i*2+1, padx=5)
            self.entries.append(entry)

        ttk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=0, column=6, padx=10)
        ttk.Button(input_frame, text="Delete Selected", command=self.delete_process).grid(row=0, column=7)

        # Table Section
        self.tree = ttk.Treeview(main_frame, columns=("PID", "Arrival", "Burst", "TAT", "WT"), show="headings", height=8)
        for col in ("PID", "Arrival", "Burst", "TAT", "WT"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, pady=10)

        # Control Section
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.algo_var = tk.StringVar(value="SJF")
        ttk.Radiobutton(ctrl_frame, text="SJF (Non-Preemptive)", variable=self.algo_var, value="SJF").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(ctrl_frame, text="SRTF (Preemptive)", variable=self.algo_var, value="SRTF").pack(side=tk.LEFT, padx=10)

        ttk.Button(ctrl_frame, text="RUN SCHEDULER", command=self.run_scheduler, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(ctrl_frame, text="RESET", command=self.clear_all).pack(side=tk.RIGHT, padx=5)

        # Summary Section
        self.summary_label = ttk.Label(main_frame, text="", font=("Arial", 10, "bold"), foreground="blue")
        self.summary_label.pack(pady=10)

    def add_process(self):
        try:
            vals = [float(e.get()) for e in self.entries]
            self.tree.insert("", tk.END, values=(int(vals[0]), vals[1], vals[2], "-", "-"))
            for e in self.entries: e.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Please fill all fields with numbers")

    def delete_process(self):
        for s in self.tree.selection(): self.tree.delete(s)

    def clear_all(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.summary_label.config(text="")

    def run_scheduler(self):
        items = self.tree.get_children()
        if not items: return
        
        procs = []
        for item in items:
            v = self.tree.item(item)['values']
            procs.append([int(v[0]), float(v[1]), float(v[2])])

        algo = self.algo_var.get()
        schedule = sjf(procs) if algo == "SJF" else srtf(procs)
        
        # Calculate Metrics
        arrival = {p[0]: p[1] for p in procs}
        burst = {p[0]: p[2] for p in procs}
        completion = {pid: end for pid, start, end in schedule}
        
        total_tat, total_wt = 0, 0
        for item in items:
            pid = self.tree.item(item)['values'][0]
            tat = round(completion[pid] - arrival[pid], 2)
            wt = round(tat - burst[pid], 2)
            total_tat += tat
            total_wt += wt
            self.tree.set(item, column="TAT", value=tat)
            self.tree.set(item, column="WT", value=wt)

        n = len(procs)
        self.summary_label.config(text=f"Average TAT: {total_tat/n:.2f}  |  Average WT: {total_wt/n:.2f}")
        
        self.draw_gantt(schedule, algo)

    def draw_gantt(self, schedule, title):
        plt.figure(figsize=(10, 4))
        colors = plt.cm.get_cmap('Pastel1', 10)
        for pid, start, end in schedule:
            plt.barh(1, end - start, left=start, edgecolor="black", color=colors(pid % 10))
            plt.text((start + end) / 2, 1, f"P{pid}", ha="center", va="center", weight='bold')
        
        plt.title(f"Gantt Chart: {title} Algorithm")
        plt.xlabel("Time Units")
        plt.yticks([])
        plt.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    # تحسين شكل الأزرار قليلاً
    style = ttk.Style()
    style.configure("Accent.TButton", font=('Arial', 10, 'bold'))
    app = SchedulerApp(root)
    root.mainloop()