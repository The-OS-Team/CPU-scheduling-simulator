"""Report generation for simulation results."""


class Report:
    """Generates formatted reports from metrics."""
    
    def __init__(self, metrics):
        self.metrics = metrics
    
    def print_process_summary(self):
        """Print summary for each process."""
        print("\n" + "="*70)
        print("PROCESS EXECUTION SUMMARY")
        print("="*70)
        print(f"{'PID':<5} {'AT':<5} {'BT':<5} {'ST':<5} {'FT':<5} {'TAT':<8} {'WT':<8} {'RT':<8}")
        print("-"*70)
        
        for p in self.metrics.completed:
            tat = self.metrics.get_turnaround_time(p)
            wt  = self.metrics.get_waiting_time(p)
            rt  = self.metrics.get_response_time(p)
    
            print(f"{p.pid:<5} {p.arrival_time:<5} {p.total_burst:<5} "
                  f"{str(p.start_time):<5} {str(p.finish_time):<5} "
                  f"{tat if tat is not None else 'N/A':<8} "
                  f"{wt if wt is not None else 'N/A':<8} "
                  f"{rt if rt is not None else 'N/A':<8}")

    def print_statistics(self):
        """Print overall statistics."""
        print("\n" + "="*70)
        print("STATISTICS")
        print("="*70)
        print(f"Total Processes: {len(self.metrics.completed)}")
        print(f"Average Turnaround Time: {self.metrics.get_avg_turnaround():.2f}")
        print(f"Average Waiting Time: {self.metrics.get_avg_waiting():.2f}")
        print(f"Average Response Time: {self.metrics.get_avg_response():.2f}")
        print(f"CPU Utilization: {self.metrics.get_cpu_utilization():.2f}%")
        print(f"Total Time: {self.metrics.total_time}")
        print("="*70)

    def print_analysis(self):
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
    
        avg_tat = self.metrics.get_avg_turnaround()
        avg_wt = self.metrics.get_avg_waiting()
        avg_rt = self.metrics.get_avg_response()
        
        print(f"- Average Turnaround Time indicates system efficiency: {avg_tat:.2f}")
        print(f"- Waiting time reflects scheduling fairness: {avg_wt:.2f}")
        print(f"- Response time shows interactivity: {avg_rt:.2f}")

        if avg_wt > avg_rt:
            print("- Observation: Processes spend significant time waiting before first execution.")
        if self.metrics.get_cpu_utilization() < 100:
            print("- CPU idle time detected → scheduling inefficiency or sparse workload.")
        else:
            print("- CPU fully utilized → good workload saturation.")

    def print_config(self, config):
        print("\n" + "="*70)
        print("SIMULATION CONFIGURATION")
        print("="*70)
        print(f"Scheduler: {config.scheduler_type}")
        print(f"Processes: {config.num_processes}")
        print(f"Burst Range: {config.burst_range}")
        print("="*70)

    def print_full_report(self, config=None):
        """Print complete report."""
        if config:
            self.print_config(config)

        self.print_process_summary()
        self.print_statistics()
        # self.print_analysis()
