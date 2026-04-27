import matplotlib.pyplot as plt
import matplotlib.cm as cm

def compress_timeline(timeline):
    if not timeline:
        return []
    
    compressed = [timeline[0]]
    
    for pid, start, end in timeline[1:]:
        last_pid, last_start, last_end = compressed[-1]
        
        if pid == last_pid:
            compressed[-1] = (last_pid, last_start, end)
        else:
            compressed.append((pid, start, end))
    
    return compressed


def print_gantt(timeline):
    timeline = compress_timeline(timeline)
    
    print("\n" + "="*70)
    print("GANTT CHART")
    print("="*70)
    
    chart = ""
    for pid, _, _ in timeline:
        label = f"P{pid}" if pid != "IDLE" else "IDLE"
        chart += f"| {label} "
    chart += "|"
    
    print(chart)
    
    time_line = f"{timeline[0][1]}"
    
    for pid, start, end in timeline:
        label = f"P{pid}" if pid != "IDLE" else "IDLE"
        space = len(label) + 3
        time_line += " " * (space - len(str(end))) + str(end)
    
    print(time_line)


import matplotlib.pyplot as plt
import matplotlib.cm as cm


def plot_gantt(timeline):
    fig, ax = plt.subplots()

    # CPU IDLE
    IDLE_PID = 0

    # Collect all processes
    all_pids = sorted(set(pid for pid, _, _ in timeline))

    # Assign consistent colors
    colormap = cm.get_cmap("tab10")

    pid_to_color = {
        pid: colormap(i % 10)
        for i, pid in enumerate(all_pids)
    }

    pid_to_color[IDLE_PID] = 'lightgray'

    # Y-axis mapping (same as before)
    y_map = {}
    y_counter = 0

    for pid, start, end in timeline:
        is_idle = (pid == IDLE_PID)

        if pid not in y_map:
            y_map[pid] = y_counter
            y_counter += 1

        ax.barh(
            y_map[pid],
            end - start,
            left=start,
            color=pid_to_color[pid],  
            edgecolor="black",
            alpha =0.6 if is_idle else 1.0,
            hatch="///" if is_idle else None
        )

    # Labels
    ax.set_yticks(list(y_map.values()))
    ax.set_yticklabels([f"P{p}" for p in y_map.keys()])

    ax.set_xlabel("Time")
    ax.set_title("Process-wise Gantt Chart")

    plt.tight_layout()
    plt.savefig("docs/plot.png", bbox_inches="tight")


def plot_overlay_gantt(srtf_timeline, priority_timeline):
    fig, ax = plt.subplots()

    # CPU IDLE
    IDLE_PID  = 0

    # Build global process set
    all_pids = set()

    for pid, _, _ in srtf_timeline:
        all_pids.add(pid)

    for pid, _, _ in priority_timeline:
        all_pids.add(pid)

    # Assign consistent colors
    colormap = cm.get_cmap("tab10")  # good discrete palette

    pid_to_color = {
        pid: colormap(i % 10)
        for i, pid in enumerate(sorted(all_pids))
    }

    pid_to_color[IDLE_PID] = 'lightgray'

    #  Y-axis mapping (same as before)
    y_map = {
        "SRTF": {},
        "PRIORITY": {}
    }

    y_counter = 0

    def get_y(label, pid):
        nonlocal y_counter

        if pid not in y_map[label]:
            y_map[label][pid] = y_counter
            y_counter += 1

        return y_map[label][pid]

    # Plot SRTF
    for pid, start, end in srtf_timeline:
        ax.barh(
            get_y("SRTF", pid),
            end - start,
            left=start,
            color=pid_to_color[pid],
            edgecolor="black"
        )

    # Plot PRIORITY
    for pid, start, end in priority_timeline:
        ax.barh(
            get_y("PRIORITY", pid),
            end - start,
            left=start,
            color=pid_to_color[pid],
            edgecolor="black"
        )

    yticks = []
    ylabels = []

    for scheduler in ["SRTF", "PRIORITY"]:
        for pid, y in y_map[scheduler].items():
            yticks.append(y)
            ylabels.append(f"{scheduler}-P{pid}")

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)

    ax.set_xlabel("Time")
    ax.set_title("SRTF vs Priority Gantt Overlay")

    plt.tight_layout()
    plt.savefig("docs/comparison.png", bbox_inches="tight")
    # plt.show()
