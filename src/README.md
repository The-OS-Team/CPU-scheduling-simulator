# CPU Scheduling Simulator

## Overview

This project implements and compares classical CPU scheduling algorithms using a unified time-driven simulation engine.

The simulator focuses on:

* Correct scheduling behavior
* Fair algorithm comparison
* Execution visualization
* Scheduling metrics analysis

Implemented algorithms:

* SJF (Shortest Job First)
* SRTF (Shortest Remaining Time First)
* Priority Scheduling (Preemptive)

---

# Features

* Time-driven simulation engine
* Preemptive and non-preemptive scheduling
* Heap-based scheduler optimization using `heapq`
* Gantt chart generation
* Waiting Time (WT), Turnaround Time (TAT), and Response Time (RT) calculations
* CPU utilization tracking
* Deterministic workloads for algorithm discussion
* Random workload generation with reproducible seeds
* Scheduler comparison mode

---

# Algorithms

## 1. SJF — Shortest Job First

Non-preemptive scheduling algorithm.

The process with the smallest burst time is selected first.

Characteristics:

* Simple
* Efficient for average waiting time
* Can suffer from starvation

---

## 2. SRTF — Shortest Remaining Time First

Preemptive version of SJF.

Whenever a process arrives with a smaller remaining burst time, the currently running process is preempted.

Characteristics:

* Minimizes average waiting time
* Highly responsive for short jobs
* May starve long processes

---

## 3. Priority Scheduling

Preemptive priority-based scheduling.

Lower priority value means higher scheduling priority.

Example:

Priority 1 > Priority 5

Characteristics:

* Useful for critical tasks
* Policy-driven scheduling
* Can cause starvation for low-priority processes

Tie-breaking order:

1. Priority
2. Arrival time
3. PID

---

# Project Structure

```text
src/
├── core/
│   └── engine.py
├── schedulers/
│   ├── sjf.py
│   ├── srtf.py
│   └── priority.py
├── models/
├── utils/
│   ├── generator.py
│   └── workloads.py
└── main.py
```

---

# Scheduling Metrics

## Turnaround Time

TAT = Finish\ Time - Arrival\ Time

## Waiting Time

WT = TAT - Burst\ Time

## Response Time

RT = First\ Run\ Time - Arrival\ Time

---

# Installation

Run from the project root:

```bash
python -m src.main
```

---

# Usage

## Run Single Scheduler

```bash
python -m src.main --sched srtf --p 10
```

---

## Compare SRTF vs Priority

```bash
python -m src.main --compare --p 10
```

---

## Deterministic Comparison

```bash
python -m src.main --compare --workload conflict
```

---

# Command Line Arguments

| Argument     | Description                                           |
| ------------ | ----------------------------------------------------- |
| `--p`        | Number of processes                                   |
| `--sched`    | Scheduler type (`sjf`, `srtf`, `priority`)            |
| `--mode`     | Workload mode (`simultaneous`, `staggered`, `random`) |
| `--compare`  | Compare SRTF and Priority                             |
| `--seed`     | Random seed                                           |
| `--workload` | Predefined deterministic workload                     |

---

# Predefined Workloads

## balanced

General workload for normal comparison.

## conflict

Demonstrates conflict between:

* burst-time optimization
* priority-based service

## starvation

Demonstrates starvation risk in Priority Scheduling.

## simultaneous

All processes arrive at the same time.

## ties

Validates deterministic tie-breaking behavior.

---

# Design Decisions

## Heap-Based Scheduling

Schedulers use Python `heapq` min-heaps.

Complexities:

* insertion: O(log n)
* extraction: O(log n)

This is more efficient than repeatedly sorting queues.

---

## Unified Engine Architecture

The engine controls:

* execution
* process lifecycle
* finishing
* requeueing
* clock progression

Schedulers only decide:

* next process
* execution slice

This creates a clean separation of responsibilities.

---

# Results Summary

In most workloads:

* SRTF achieves lower WT and TAT
* Priority Scheduling favors important tasks
* CPU utilization remains similar across algorithms

Example conclusion:

SRTF generally performs better for average responsiveness and waiting time. However, Priority Scheduling remains important in systems where task importance is more critical than average performance.

---

# Starvation Discussion

Both SRTF and Priority Scheduling may cause starvation.

Examples:

* Long jobs in SRTF
* Low-priority jobs in Priority Scheduling

Real operating systems often use:

* aging
* dynamic priorities
* multi-level queues

to reduce starvation risk.

---

# Assumptions

* Single-core CPU
* No I/O blocking
* No context-switch overhead
* Known burst times
* Deterministic process execution

---

# Authors

Operating Systems Scheduling Project

