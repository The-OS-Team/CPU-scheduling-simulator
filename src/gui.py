"""
CPU Scheduling Simulator — upgraded GUI
All backend imports (SimulationRunner, SimulationConfig, Process, plot_gantt) unchanged.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import copy

from src.simulation.runner import SimulationRunner
from src.simulation.config import SimulationConfig
from src.simulation.comparison import ComparisonRunner
from src.models.process import Process
from src.utils.gantt import plot_gantt, plot_overlay_gantt
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
ACCENT_DIM    = "#2a3f6e"
ACCENT_HOVER  = "#3a74d4"
ACCENT2       = "#3ecf8e"
ACCENT2_DIM   = "#1a4a35"
DANGER        = "#e85d75"
DANGER_DIM    = "#4a1e28"
COMPARE_COLOR = "#c97cf4"
COMPARE_DIM   = "#3a1f5e"
TEXT_PRI      = "#e8eaf0"
TEXT_SEC      = "#8b90a8"
BORDER        = "#2e3450"

PROCESS_COLORS = [
    "#4e8ef7", "#3ecf8e", "#f97b4e", "#c97cf4",
    "#f7c948", "#4ecbf9", "#f74e8e", "#8ef74e",
]

ALGO_LABELS = [("SJF", "sjf"),("Priority", "priority") ,("SRTF", "srtf")]


class ProcessCard(ctk.CTkFrame):
    """A single process row in the queue list."""

    def __init__(self, master, proc: dict, index: int, on_delete, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10, **kwargs)
        self.configure(border_width=1, border_color=BORDER)

        color = PROCESS_COLORS[index % len(PROCESS_COLORS)]

        accent = ctk.CTkFrame(self, width=4, fg_color=color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(0, 10))

        badge = ctk.CTkLabel(
            self, text=f"P{proc['pid']}",
            width=36, height=36,
            fg_color=BG_INPUT, text_color=color,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=18,
        )
        badge.pack(side="left", padx=(0, 10), pady=8)

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

    def __init__(self, master, label: str, accent_color=None, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, **kwargs)
        self.configure(border_width=1, border_color=BORDER)
        self._accent = accent_color or ACCENT

        self.value_label = ctk.CTkLabel(
            self, text="—",
            text_color=self._accent,
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


class CompareMetricCard(ctk.CTkFrame):
    """A metric card that shows two values side by side for comparison."""

    def __init__(self, master, label: str, algo_a: str, algo_b: str, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, **kwargs)
        self.configure(border_width=1, border_color=BORDER)

        # Label at top
        ctk.CTkLabel(
            self, text=label,
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=11),
        ).pack(pady=(10, 4))

        # Side by side values
        vals_frame = ctk.CTkFrame(self, fg_color="transparent")
        vals_frame.pack(fill="x", padx=8, pady=(0, 10))

        # Left (algo A)
        left = ctk.CTkFrame(vals_frame, fg_color=BG_INPUT, corner_radius=8)
        left.pack(side="left", expand=True, fill="x", padx=(0, 4))

        ctk.CTkLabel(
            left, text=algo_a.upper(),
            text_color=ACCENT,
            font=ctk.CTkFont(size=9, weight="bold"),
        ).pack(pady=(6, 0))

        self.val_a = ctk.CTkLabel(
            left, text="—",
            text_color=ACCENT,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.val_a.pack(pady=(0, 6))

        # Right (algo B)
        right = ctk.CTkFrame(vals_frame, fg_color=BG_INPUT, corner_radius=8)
        right.pack(side="left", expand=True, fill="x", padx=(4, 0))

        ctk.CTkLabel(
            right, text=algo_b.upper(),
            text_color=COMPARE_COLOR,
            font=ctk.CTkFont(size=9, weight="bold"),
        ).pack(pady=(6, 0))

        self.val_b = ctk.CTkLabel(
            right, text="—",
            text_color=COMPARE_COLOR,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.val_b.pack(pady=(0, 6))

    def set(self, val_a: str, val_b: str):
        self.val_a.configure(text=val_a)
        self.val_b.configure(text=val_b)


class SchedulerGUI:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1200x800")
        self.root.configure(fg_color=BG_BASE)
        self.root.minsize(960, 660)

        self.processes: list[dict] = []
        self._pid_counter = 1
        self._canvas = None
        self._compare_mode = False

        # Input vars
        self.arrival_var   = tk.StringVar(value="0")
        self.burst_var     = tk.StringVar(value="4")
        self.priority_var  = tk.StringVar(value="1")
        self.quantum_var   = tk.StringVar(value="2")
        self.scheduler_var = tk.StringVar(value="sjf")

        # Compare algo selectors
        self.compare_algo_a = tk.StringVar(value="sjf")
        self.compare_algo_b = tk.StringVar(value="priority")

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

        # Left sidebar — outer shell keeps the fixed width; inner scrollable holds content
        sidebar_shell = ctk.CTkFrame(body, width=310, fg_color=BG_PANEL, corner_radius=14)
        sidebar_shell.pack(side="left", fill="y", padx=(0, 12))
        sidebar_shell.pack_propagate(False)

        sidebar = ctk.CTkScrollableFrame(
            sidebar_shell, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT_DIM,
        )
        sidebar.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_sidebar(sidebar)

        # Right main
        main = ctk.CTkFrame(body, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)

        self._build_main(main)

    def _build_sidebar(self, parent):
        pad = {"padx": 16}

        # ── Mode toggle ────────────────────────────────────────────────────────
        mode_frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10)
        mode_frame.pack(fill="x", padx=16, pady=(16, 0))

        self._single_btn = ctk.CTkButton(
            mode_frame, text="Single", height=30,
            fg_color=ACCENT_DIM, hover_color=ACCENT_DIM,
            text_color=ACCENT, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self._set_single_mode,
        )
        self._single_btn.pack(side="left", expand=True, fill="x", padx=4, pady=4)

        self._compare_btn = ctk.CTkButton(
            mode_frame, text="⇄ Compare", height=30,
            fg_color="transparent", hover_color=COMPARE_DIM,
            text_color=TEXT_SEC, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self._set_compare_mode,
        )
        self._compare_btn.pack(side="left", expand=True, fill="x", padx=4, pady=4)

        # ── Algo slot — single and compare frames live here, one shown at a time
        self._algo_slot = ctk.CTkFrame(parent, fg_color="transparent")
        self._algo_slot.pack(fill="x")

        # Single mode: three buttons in one horizontal row — fits fine at full width
        self._single_algo_frame = ctk.CTkFrame(self._algo_slot, fg_color="transparent")

        ctk.CTkLabel(
            self._single_algo_frame, text="ALGORITHM",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", pady=(14, 6), **pad)

        algo_row = ctk.CTkFrame(self._single_algo_frame, fg_color=BG_CARD, corner_radius=10)
        algo_row.pack(fill="x", **pad)
        self._algo_btns = {}
        for label, val in ALGO_LABELS:
            btn = ctk.CTkButton(
                algo_row, text=label, height=32,
                fg_color="transparent", hover_color=ACCENT_DIM,
                text_color=TEXT_SEC, font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda v=val: self._select_algo(v),
            )
            btn.pack(side="left", expand=True, fill="x", padx=3, pady=4)
            self._algo_btns[val] = btn
        self._select_algo("sjf")

        # Compare mode: A and B each get their OWN full-width row of 3 buttons
        # (no "A:" label stealing width — labels sit above each row instead)
        self._compare_algo_frame = ctk.CTkFrame(self._algo_slot, fg_color="transparent")

        ctk.CTkLabel(
            self._compare_algo_frame, text="COMPARE ALGORITHMS",
            text_color=TEXT_SEC,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).pack(anchor="w", pady=(14, 4), **pad)

        # Row A
        ctk.CTkLabel(
            self._compare_algo_frame, text="Algorithm A",
            text_color=ACCENT,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=16, pady=(4, 2))

        btn_frame_a = ctk.CTkFrame(self._compare_algo_frame, fg_color=BG_CARD, corner_radius=10)
        btn_frame_a.pack(fill="x", **pad)
        self._compare_algo_a_btns = {}
        for label, val in ALGO_LABELS:
            btn = ctk.CTkButton(
                btn_frame_a, text=label, height=30,
                fg_color="transparent", hover_color=ACCENT_DIM,
                text_color=TEXT_SEC, font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda v=val: self._select_compare_a(v),
            )
            btn.pack(side="left", expand=True, fill="x", padx=3, pady=4)
            self._compare_algo_a_btns[val] = btn

        # Row B
        ctk.CTkLabel(
            self._compare_algo_frame, text="Algorithm B",
            text_color=COMPARE_COLOR,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(anchor="w", padx=16, pady=(8, 2))

        btn_frame_b = ctk.CTkFrame(self._compare_algo_frame, fg_color=BG_CARD, corner_radius=10)
        btn_frame_b.pack(fill="x", **pad)
        self._compare_algo_b_btns = {}
        for label, val in ALGO_LABELS:
            btn = ctk.CTkButton(
                btn_frame_b, text=label, height=30,
                fg_color="transparent", hover_color=COMPARE_DIM,
                text_color=TEXT_SEC, font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda v=val: self._select_compare_b(v),
            )
            btn.pack(side="left", expand=True, fill="x", padx=3, pady=4)
            self._compare_algo_b_btns[val] = btn

        self._select_compare_a("sjf")
        self._select_compare_b("priority")

        # Show single mode frame by default
        self._single_algo_frame.pack(fill="x")

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
            command=self._on_workload_selected,
            fg_color=BG_INPUT,
            button_color=ACCENT_DIM,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            dynamic_resizing=False,
        ).pack(fill="x", pady=(0, 6), **pad)
        
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

        self.queue_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent", height=160,
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

        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=12, pady=14)

        # ── Run button ─────────────────────────────────────────────────────────
        self._run_btn = ctk.CTkButton(
            parent, text="▶  Run Simulation", height=44,
            fg_color=ACCENT2, hover_color="#2fb87a",
            text_color="#0a1a12", font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            command=self.run_sim,
        )
        self._run_btn.pack(fill="x", padx=16, pady=(0, 16))

    def _build_main(self, parent):
        # ── Metrics row ────────────────────────────────────────────────────────
        self.metrics_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.metrics_container.pack(fill="x", pady=(0, 12))

        self._build_single_metrics()

        # ── Gantt chart area ───────────────────────────────────────────────────
        gantt_panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=14)
        gantt_panel.pack(fill="both", expand=True)

        self.gantt_title_label = ctk.CTkLabel(
            gantt_panel, text="Gantt Chart",
            text_color=TEXT_PRI,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.gantt_title_label.pack(anchor="w", padx=16, pady=(14, 4))

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

    def _build_single_metrics(self):
        """Build 4 single-value metric cards."""
        for w in self.metrics_container.winfo_children():
            w.destroy()

        self.metric_cards = []

        labels = ["Avg Waiting", "Avg Turnaround", "Avg Response", "CPU Util %"]
        self.metric_cards: list[MetricCard] = []
        for lbl in labels:
            card = MetricCard(self.metrics_container, lbl)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.metric_cards.append(card)

    def _build_compare_metrics(self, algo_a: str, algo_b: str):
        """Build 4 split comparison metric cards."""
        for w in self.metrics_container.winfo_children():
            w.destroy()

        self.compare_metric_cards = []

        labels = ["Avg Waiting", "Avg Turnaround", "Avg Response", "CPU Util %"]
        self.compare_metric_cards: list[CompareMetricCard] = []
        for lbl in labels:
            card = CompareMetricCard(self.metrics_container, lbl, algo_a, algo_b)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.compare_metric_cards.append(card)

    # ── MODE SWITCHING ─────────────────────────────────────────────────────────

    def _set_single_mode(self):
        self._compare_mode = False

        self.compare_metric_cards = [] # kill compare cards

        self._single_btn.configure(fg_color=ACCENT_DIM, text_color=ACCENT)
        self._compare_btn.configure(fg_color="transparent", text_color=TEXT_SEC)

        self._compare_algo_frame.pack_forget()
        self._single_algo_frame.pack(fill="x", in_=self._algo_slot)

        self._run_btn.configure(
            text="▶  Run Simulation",
            fg_color=ACCENT2, hover_color="#2fb87a",
            text_color="#0a1a12",
        )
        self.gantt_title_label.configure(text="Gantt Chart")
        self._build_single_metrics()
        self._clear_results()

    def _set_compare_mode(self):
        self._compare_mode = True

        self.metric_cards = [] # kill old single cards

        self._compare_btn.configure(fg_color=COMPARE_DIM, text_color=COMPARE_COLOR)
        self._single_btn.configure(fg_color="transparent", text_color=TEXT_SEC)

        self._single_algo_frame.pack_forget()
        self._compare_algo_frame.pack(fill="x", in_=self._algo_slot)

        self._run_btn.configure(
            text="⇄  Run Comparison",
            fg_color=COMPARE_DIM, hover_color="#4a2a7a",
            text_color=COMPARE_COLOR,
        )
        a = self.compare_algo_a.get()
        b = self.compare_algo_b.get()
        self.gantt_title_label.configure(text=f"Gantt Chart — {a.upper()} vs {b.upper()}")
        self._build_compare_metrics(a, b)
        self._clear_results()

    # ── ALGORITHM SELECTORS ────────────────────────────────────────────────────

    def _select_algo(self, val: str):
        self.scheduler_var.set(val)
        for k, btn in self._algo_btns.items():
            if k == val:
                btn.configure(fg_color=ACCENT_DIM, text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SEC)

    def _select_compare_a(self, val: str):
        self.compare_algo_a.set(val)
        for k, btn in self._compare_algo_a_btns.items():
            if k == val:
                btn.configure(fg_color=ACCENT_DIM, text_color=ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SEC)
        if self._compare_mode:
            self.gantt_title_label.configure(
                text=f"Gantt Chart — {val.upper()} vs {self.compare_algo_b.get().upper()}"
            )
            self._build_compare_metrics(val, self.compare_algo_b.get())

    def _select_compare_b(self, val: str):
        self.compare_algo_b.set(val)
        for k, btn in self._compare_algo_b_btns.items():
            if k == val:
                btn.configure(fg_color=COMPARE_DIM, text_color=COMPARE_COLOR)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SEC)
        if self._compare_mode:
            self.gantt_title_label.configure(
                text=f"Gantt Chart — {self.compare_algo_a.get().upper()} vs {val.upper()}"
            )
            self._build_compare_metrics(self.compare_algo_a.get(), val)

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

    def _on_workload_selected(self, choice):
       self.load_workload()

    def reset_all(self):
        if self.processes and not messagebox.askyesno("Reset", "Remove all processes and clear results?"):
            return
        self.processes.clear()
        self._pid_counter = 1
        self._clear_results()
        self._refresh_queue()

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

    def _apply_mpl_theme(self):
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

    def _embed_figure(self, fig):
        if self._canvas:
            self._canvas.get_tk_widget().destroy()

        if self.placeholder_label and self.placeholder_label.winfo_exists():
            self.placeholder_label.destroy()

        fig.patch.set_facecolor(BG_PANEL)
        fig.tight_layout(pad=1.5)

        self._canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_gantt(self, timeline):
        if not timeline:
            return
        self._apply_mpl_theme()
        fig = plot_gantt(timeline)
        self._embed_figure(fig)

    def show_overlay_gantt(self, timeline_a, timeline_b):
        if not timeline_a and not timeline_b:
            return
        self._apply_mpl_theme()
        fig = plot_overlay_gantt(timeline_a, timeline_b)
        self._embed_figure(fig)

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

        if hasattr(self, "metric_cards"):
            for card in self.metric_cards:
                card.set("—")

        if hasattr(self, "compare_metric_cards"):
            for card in self.compare_metric_cards:
                card.set("—", "—")

        self.status_label.configure(text="● Idle", text_color=TEXT_SEC)

    # ── RUN SIMULATION ─────────────────────────────────────────────────────────

    def _build_process_objects(self) -> list[Process]:
        return [
            Process(
                pid=p["pid"],
                arrival_time=p["arrival_time"],
                burst_time=p["burst_time"],
                priority=p.get("priority", 0),
            )
            for p in self.processes
        ]

    def run_sim(self):
        if not self.processes:
            messagebox.showerror("No Processes", "Add at least one process before running.")
            return

        if self._compare_mode:
            self._run_comparison()
        else:
            self._run_single()

    def _run_single(self):
        process_objs = self._build_process_objects()
        config = SimulationConfig()
        config.set_scheduler(self.scheduler_var.get())
        runner = SimulationRunner(config)

        try:
            self.status_label.configure(text="● Running…", text_color="#f7c948")
            self.root.update_idletasks()

            completed      = runner.run(process_objs)
            report         = runner.get_report()
            metrics        = report.metrics

            self.metric_cards[0].set(f"{metrics.get_avg_waiting():.2f}")
            self.metric_cards[1].set(f"{metrics.get_avg_turnaround():.2f}")
            self.metric_cards[2].set(f"{metrics.get_avg_response():.2f}")
            self.metric_cards[3].set(f"{metrics.get_cpu_utilization():.1f}%")

            self.show_gantt(runner.timeline)

            self.status_label.configure(
                text=f"● Done — {len(completed)} processes",
                text_color=ACCENT2,
            )

        except Exception as e:
            self.status_label.configure(text="● Error", text_color=DANGER)
            messagebox.showerror("Simulation Error", str(e))

    def _run_comparison(self):
        algo_a = self.compare_algo_a.get()
        algo_b = self.compare_algo_b.get()

        if algo_a == algo_b:
            messagebox.showerror(
                "Same Algorithm",
                "Please select two different algorithms to compare."
            )
            return

        process_objs = self._build_process_objects()
        config = SimulationConfig()

        try:
            self.status_label.configure(text="● Comparing…", text_color="#f7c948")
            self.root.update_idletasks()

            comp_runner = ComparisonRunner(config)
            results = comp_runner.run_all([algo_a, algo_b], processes=process_objs)

            data_a = results[algo_a]
            data_b = results[algo_b]

            self.compare_metric_cards[0].set(f"{data_a['avg_wt']:.2f}",  f"{data_b['avg_wt']:.2f}")
            self.compare_metric_cards[1].set(f"{data_a['avg_tat']:.2f}", f"{data_b['avg_tat']:.2f}")
            self.compare_metric_cards[2].set(f"{data_a['avg_rt']:.2f}",  f"{data_b['avg_rt']:.2f}")
            self.compare_metric_cards[3].set(f"{data_a['cpu']:.1f}%",    f"{data_b['cpu']:.1f}%")

            self.show_overlay_gantt(
                data_a["timeline"], data_b["timeline"],
            )

            self.status_label.configure(
                text=f"● Done — {algo_a.upper()} vs {algo_b.upper()}",
                text_color=COMPARE_COLOR,
            )

        except Exception as e:
            self.status_label.configure(text="● Error", text_color=DANGER)
            messagebox.showerror("Comparison Error", str(e))


if __name__ == "__main__":
    root = ctk.CTk()
    app = SchedulerGUI(root)
    root.mainloop()
