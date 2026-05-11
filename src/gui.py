"""
CPU Scheduling Simulator — upgraded GUI
All backend imports (SimulationRunner, SimulationConfig, Process, plot_gantt) unchanged.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from src.simulation.runner import SimulationRunner
from src.simulation.config import SimulationConfig
from src.models.process import Process
from src.utils.gantt import plot_gantt
from src.utils.workloads import get_workload

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Palette
BG_BASE    = "#0f1117"
BG_PANEL   = "#1a1d27"
BG_CARD    = "#21253a"
BG_INPUT   = "#2a2f45"
ACCENT        = "#4e8ef7"
ACCENT_DIM    = "#2a3f6e"   # solid stand-in for ACCENT + alpha
ACCENT_HOVER  = "#3a74d4"
ACCENT2       = "#3ecf8e"
DANGER        = "#e85d75"
DANGER_DIM    = "#4a1e28"   # solid stand-in for DANGER + alpha
TEXT_PRI      = "#e8eaf0"
TEXT_SEC      = "#8b90a8"
BORDER        = "#2e3450"

PROCESS_COLORS = [
    "#4e8ef7", "#3ecf8e", "#f97b4e", "#c97cf4",
    "#f7c948", "#4ecbf9", "#f74e8e", "#8ef74e",
]


class ProcessCard(ctk.CTkFrame):
    """A single process row in the queue list."""

    def __init__(self, master, proc: dict, index: int, on_delete, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10, **kwargs)
        self.configure(border_width=1, border_color=BORDER)

        color = PROCESS_COLORS[index % len(PROCESS_COLORS)]

        # Color accent bar
        accent = ctk.CTkFrame(self, width=4, fg_color=color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 10))

        # PID badge
        badge = ctk.CTkLabel(
            self, text=f"P{proc['pid']}",
            width=36, height=36,
            fg_color=BG_INPUT, text_color=color,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=18,
        )
        badge.pack(side="left", padx=(0, 10), pady=8)

        # Info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=6)

        ctk.CTkLabel(
            info_frame,
            text=f"P{proc['pid']} — Arrival: {proc['arrival_time']}  Burst: {proc['burst_time']}  Priority: {proc['priority']}",
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=12),
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=f"Burst time: {proc['burst_time']} units",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=11),
            anchor="w",
        ).pack(anchor="w")

        # Delete button
        del_btn = ctk.CTkButton(
            self, text="✕", width=28, height=28,
            fg_color="transparent", hover_color=DANGER_DIM,
            text_color=TEXT_SEC, font=ctk.CTkFont(size=13),
            corner_radius=6,
            command=on_delete,
        )
        del_btn.pack(side="right", padx=8, pady=8)


class MetricCard(ctk.CTkFrame):
    """A metric display card."""

    def __init__(self, master, label: str, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, **kwargs)
        self.configure(border_width=1, border_color=BORDER)

        self.value_label = ctk.CTkLabel(
            self, text="—",
            text_color=ACCENT,
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.value_label.pack(pady=(14, 2))

        ctk.CTkLabel(
            self, text=label,
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=11),
        ).pack(pady=(0, 14))

    def set(self, val: str):
        self.value_label.configure(text=val)


class SchedulerGUI:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1100x760")
        self.root.configure(fg_color=BG_BASE)
        self.root.minsize(900, 640)

        self.processes: list[dict] = []
        self._pid_counter = 1
        self._canvas = None

        # Input vars (keep same types as original)
        self.arrival_var  = tk.StringVar(value="0")
        self.burst_var    = tk.StringVar(value="4")
        self.priority_var = tk.StringVar(value="1")
        self.quantum_var  = tk.StringVar(value="2")
        self.scheduler_var = tk.StringVar(value="srtf")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.root.quit()
        self.root.destroy()

    # ── UI BUILD ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color=BG_PANEL, height=56, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="⚙  CPU Scheduling Simulator",
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left", padx=20, pady=14)

        self.status_label = ctk.CTkLabel(
            header, text="● Idle",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=12),
        )
        self.status_label.pack(side="right", padx=20)

        # Body
        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Left sidebar
        sidebar = ctk.CTkFrame(body, width=300, fg_color=BG_PANEL, corner_radius=14)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        self._build_sidebar(sidebar)

        # Right main
        main = ctk.CTkFrame(body, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)

        self._build_main(main)

    def _build_sidebar(self, parent):
        pad = {"padx": 16}

        # ── Algorithm ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            parent, text="ALGORITHM",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", pady=(18, 6), **pad)

        algos = [("SRTF", "srtf"), ("Priority", "priority")]
        algo_frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10)
        algo_frame.pack(fill="x", **pad)
        self._algo_btns = {}
        for label, val in algos:
            btn = ctk.CTkButton(
                algo_frame, text=label, height=32,
                fg_color="transparent", hover_color=ACCENT_DIM,
                text_color=TEXT_SEC, font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda v=val: self._select_algo(v),
            )
            btn.pack(side="left", expand=True, fill="x", padx=4, pady=4)
            self._algo_btns[val] = btn
        self._select_algo("srtf")

        # Separator
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=14)

        # ── Process inputs ─────────────────────────────────────────────────────
        ctk.CTkLabel(
            parent, text="NEW PROCESS",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", pady=(0, 8), **pad)

        fields = [
            ("Arrival Time", self.arrival_var),
            ("Burst Time",   self.burst_var),
            ("Priority",     self.priority_var),
        ]
        for label, var in fields:
            ctk.CTkLabel(
                parent, text=label,
                text_color=TEXT_SEC, font=ctk.CTkFont(size=12), anchor="w",
            ).pack(anchor="w", **pad)
            ctk.CTkEntry(
                parent, textvariable=var, height=36,
                fg_color=BG_INPUT, border_color=BORDER,
                text_color=TEXT_PRI, font=ctk.CTkFont(size=13),
                corner_radius=8,
            ).pack(fill="x", pady=(2, 8), **pad)

        ctk.CTkButton(
            parent, text="＋  Add Process", height=38,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            command=self.add_process,
        ).pack(fill="x", pady=(0, 4), **pad)

        # ── Workload presets ───────────────────────────────────────────────────
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            parent, text="LOAD PRESET WORKLOAD",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", pady=(0, 6), **pad)

        WORKLOAD_OPTIONS = {
            "balanced    — mixed burst/priority":   "balanced",
            "conflict    — priority vs burst":      "conflict",
            "starvation  — fairness stress":        "starvation",
            "ties        — tie-breaking":           "ties",
            "simultaneous — all arrive at t=0":    "simultaneous",
        }
        self._workload_labels = list(WORKLOAD_OPTIONS.keys())
        self._workload_keys   = WORKLOAD_OPTIONS

        self._workload_var = tk.StringVar(value=self._workload_labels[0])
        ctk.CTkOptionMenu(
            parent,
            variable=self._workload_var,
            values=self._workload_labels,
            fg_color=BG_INPUT,
            button_color=ACCENT_DIM,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            dynamic_resizing=False,
        ).pack(fill="x", pady=(0, 6), **pad)

        ctk.CTkButton(
            parent, text="⬇  Load Workload", height=34,
            fg_color=BG_CARD, hover_color=ACCENT_DIM,
            text_color=ACCENT, border_width=1, border_color=ACCENT_DIM,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            command=self.load_workload,
        ).pack(fill="x", pady=(0, 4), **pad)

        # Separator
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=12)

        # ── Process queue ──────────────────────────────────────────────────────
        queue_header = ctk.CTkFrame(parent, fg_color="transparent")
        queue_header.pack(fill="x", **pad)

        ctk.CTkLabel(
            queue_header, text="PROCESS QUEUE",
            text_color=TEXT_SEC, font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            queue_header, text="Reset All", width=70, height=24,
            fg_color="transparent", hover_color=DANGER_DIM,
            text_color=DANGER, font=ctk.CTkFont(size=11),
            border_width=1, border_color=DANGER,
            corner_radius=6,
            command=self.reset_all,
        ).pack(side="right")

        # Scrollable list
        self.queue_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent", height=180,
        )
        self.queue_scroll.pack(fill="x", pady=(8, 0), padx=12)

        self.empty_label = ctk.CTkLabel(
            self.queue_scroll,
            text="No processes yet.\nAdd one above.",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=12),
            justify="center",
        )
        self.empty_label.pack(pady=20)

        # Separator
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=14)

        # ── Run button ─────────────────────────────────────────────────────────
        ctk.CTkButton(
            parent, text="▶  Run Simulation", height=44,
            fg_color=ACCENT2, hover_color="#2fb87a",
            text_color="#0a1a12", font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            command=self.run_sim,
        ).pack(fill="x", padx=16, pady=(0, 16))

    def _build_main(self, parent):
        # ── Metrics row ────────────────────────────────────────────────────────
        metrics_row = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_row.pack(fill="x", pady=(0, 12))

        labels = ["Avg Waiting", "Avg Turnaround", "Avg Response", "CPU Util %"]
        self.metric_cards: list[MetricCard] = []
        for lbl in labels:
            card = MetricCard(metrics_row, lbl)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.metric_cards.append(card)

        # ── Gantt chart area ───────────────────────────────────────────────────
        gantt_panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=14)
        gantt_panel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            gantt_panel, text="Gantt Chart",
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkFrame(gantt_panel, height=1, fg_color=BORDER).pack(fill="x", padx=12)

        self.chart_frame = ctk.CTkFrame(gantt_panel, fg_color="transparent")
        self.chart_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.placeholder_label = ctk.CTkLabel(
            self.chart_frame,
            text="Run a simulation to see the Gantt chart here.",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=13),
        )
        self.placeholder_label.pack(expand=True)

    # ── ALGORITHM SELECTOR ─────────────────────────────────────────────────────

    def _select_algo(self, val: str):
        self.scheduler_var.set(val)
        for k, btn in self._algo_btns.items():
            if k == val:
                btn.configure(fg_color=ACCENT_DIM, text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SEC)

    # ── PROCESS HANDLING ───────────────────────────────────────────────────────

    def add_process(self):
        try:
            arrival  = int(self.arrival_var.get())
            burst    = int(self.burst_var.get())
            priority = int(self.priority_var.get())
            if burst < 1:
                raise ValueError("Burst must be ≥ 1")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e) or "Please enter valid integers.")
            return

        proc = {
            "pid":          self._pid_counter,
            "arrival_time": arrival,
            "burst_time":   burst,
            "priority":     priority,
        }
        self.processes.append(proc)
        self._pid_counter += 1
        self._refresh_queue()

    def delete_process(self, pid: int):
        self.processes = [p for p in self.processes if p["pid"] != pid]
        self._refresh_queue()

    def load_workload(self):
        label = self._workload_var.get()
        key   = self._workload_keys[label]
        try:
            procs = get_workload(key)
        except ValueError as e:
            messagebox.showerror("Workload Error", str(e))
            return

        if self.processes:
            if not messagebox.askyesno(
                "Load Workload",
                f"Replace the current queue with the '{key}' workload?"
            ):
                return

        self.processes.clear()
        self._pid_counter = 1
        for p in procs:
            self.processes.append({
                "pid":          self._pid_counter,
                "arrival_time": p.arrival_time,
                "burst_time":   p.total_burst,
                "priority":     p.priority,
            })
            self._pid_counter += 1
        self._refresh_queue()

    def reset_all(self):
        if self.processes and not messagebox.askyesno("Reset", "Remove all processes and clear results?"):
            return
        self.processes.clear()
        self._pid_counter = 1
        self._refresh_queue()
        self._clear_results()

    def _refresh_queue(self):
        for widget in self.queue_scroll.winfo_children():
            widget.destroy()

        if not self.processes:
            self.empty_label = ctk.CTkLabel(
                self.queue_scroll,
                text="No processes yet.\nAdd one above.",
                text_color=TEXT_SEC,
                font=ctk.CTkFont(size=12),
                justify="center",
            )
            self.empty_label.pack(pady=20)
            return

        for i, proc in enumerate(self.processes):
            card = ProcessCard(
                self.queue_scroll, proc, i,
                on_delete=lambda p=proc["pid"]: self.delete_process(p),
            )
            card.pack(fill="x", pady=(0, 6))

    # ── CHART ──────────────────────────────────────────────────────────────────

    def show_gantt(self, timeline):
        if not timeline:
            return

        # Style matplotlib to match dark theme
        plt.rcParams.update({
            "figure.facecolor":  BG_PANEL,
            "axes.facecolor":    BG_CARD,
            "axes.edgecolor":    BORDER,
            "axes.labelcolor":   TEXT_SEC,
            "xtick.color":       TEXT_SEC,
            "ytick.color":       TEXT_SEC,
            "text.color":        TEXT_PRI,
            "grid.color":        BORDER,
        })

        if self._canvas:
            self._canvas.get_tk_widget().destroy()

        if self.placeholder_label and self.placeholder_label.winfo_exists():
            self.placeholder_label.destroy()

        fig = plot_gantt(timeline)
        fig.patch.set_facecolor(BG_PANEL)
        fig.tight_layout(pad=1.5)

        self._canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def _clear_results(self):
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.placeholder_label = ctk.CTkLabel(
            self.chart_frame,
            text="Run a simulation to see the Gantt chart here.",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=13),
        )
        self.placeholder_label.pack(expand=True)

        for card in self.metric_cards:
            card.set("—")

        self.status_label.configure(text="● Idle", text_color=TEXT_SEC)

    # ── RUN SIMULATION ─────────────────────────────────────────────────────────

    def run_sim(self):
        if not self.processes:
            messagebox.showerror("No Processes", "Add at least one process before running.")
            return

        # Convert dict → Process objects (identical to original)
        process_objs = [
            Process(
                pid=p["pid"],
                arrival_time=p["arrival_time"],
                burst_time=p["burst_time"],
                priority=p.get("priority", 0),
            )
            for p in self.processes
        ]

        config = SimulationConfig()
        config.set_scheduler(self.scheduler_var.get())

        runner = SimulationRunner(config)

        try:
            self.status_label.configure(text="● Running…", text_color="#f7c948")
            self.root.update_idletasks()

            completed      = runner.run(process_objs)
            report         = runner.get_report()
            metrics        = report.metrics

            avg_waiting    = metrics.get_avg_waiting()
            avg_turnaround = metrics.get_avg_turnaround()
            avg_response   = metrics.get_avg_response()
            cpu_util       = metrics.get_cpu_utilization()

            # Update metric cards
            self.metric_cards[0].set(f"{avg_waiting:.2f}")
            self.metric_cards[1].set(f"{avg_turnaround:.2f}")
            self.metric_cards[2].set(f"{avg_response:.2f}")
            self.metric_cards[3].set(f"{cpu_util:.1f}%")

            self.show_gantt(runner.timeline)

            self.status_label.configure(
                text=f"● Done — {len(completed)} processes",
                text_color=ACCENT2,
            )

        except Exception as e:
            self.status_label.configure(text="● Error", text_color=DANGER)
            messagebox.showerror("Simulation Error", str(e))



if __name__ == "__main__":
    root = ctk.CTk()
    app = SchedulerGUI(root)
    root.mainloop()
