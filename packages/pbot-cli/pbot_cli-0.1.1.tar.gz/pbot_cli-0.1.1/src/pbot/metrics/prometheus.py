
from prometheus_client import start_http_server, Counter

COMMAND_COUNTER = Counter("pbot_command_total", "Total PBOT command runs", ["command"])

def start_metrics_server():
    start_http_server(8000)

def count_command(command_name: str):
    COMMAND_COUNTER.labels(command=command_name).inc()
