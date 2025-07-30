import denet
import json
import subprocess

from denet.analysis import save_metrics

# Execute a command with monitoring and capture the result
try:
    exit_code, monitor = denet.execute_with_monitoring(
        cmd=["ping", "8.8.8.8", "-c", "2"],
        timeout=5,
        base_interval_ms=100,
        max_interval_ms=1000,
        write_metadata=True,
        store_in_memory=True,    # Store samples in memory
        output_file='out.json',  # Optional file output
        include_children=True    # Monitor child processes (default True)
    )
    # Access collected metrics after execution
    samples = monitor.get_samples()
    print(f"Collected {len(samples)} samples")
    print(f"Exit code: {exit_code}")

    # Generate and print summary
    summary_json = monitor.get_summary()
    summary = json.loads(summary_json)
    print(f"Average CPU usage: {summary['avg_cpu_usage']}%")
    print(f"Peak memory: {summary['peak_mem_rss_kb']/1024:.2f} MB")

    save_metrics(samples, "out2.jsonl", format="jsonl", include_metadata=True)


except Exception:
    raise()
