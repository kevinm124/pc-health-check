"""PC Health Check - a quick overview of your computer's health in the terminal."""

import platform
import time
from datetime import timedelta

import psutil
from rich.console import Console
from rich.table import Table

console = Console()


def color_for(percent):
    """Pick a color based on how full/busy something is."""
    if percent < 60:
        return "green"
    if percent < 85:
        return "yellow"
    return "red"


def bar(percent, width=20):
    """Draw a simple text progress bar, e.g. ██████░░░░."""
    filled = int(width * percent / 100)
    return "█" * filled + "░" * (width - filled)


def gb(num_bytes):
    """Convert bytes to gigabytes, rounded to one decimal."""
    return f"{num_bytes / 1024**3:.1f} GB"


def build_table():
    table = Table(title="🖥️  PC Health Check", title_style="bold cyan")
    table.add_column("Component", style="bold")
    table.add_column("Usage", no_wrap=True)
    table.add_column("Details", style="dim")

    # CPU - measure over 1 second for an accurate reading
    cpu = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count(logical=False) or psutil.cpu_count()
    c = color_for(cpu)
    table.add_row("CPU", f"[{c}]{bar(cpu)} {cpu:.0f}%[/{c}]", f"{cores} cores")

    # RAM
    ram = psutil.virtual_memory()
    c = color_for(ram.percent)
    table.add_row(
        "RAM",
        f"[{c}]{bar(ram.percent)} {ram.percent:.0f}%[/{c}]",
        f"{gb(ram.used)} / {gb(ram.total)}",
    )

    # Disks - every mounted drive (C:, D: ... on Windows)
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue  # skip empty card readers, DVD drives, etc.
        if usage.total < 1024**3:
            continue  # skip tiny system partitions under 1 GB
        c = color_for(usage.percent)
        table.add_row(
            f"Disk {part.mountpoint}",
            f"[{c}]{bar(usage.percent)} {usage.percent:.0f}%[/{c}]",
            f"{gb(usage.free)} free of {gb(usage.total)}",
        )

    # Battery - only exists on laptops
    battery = psutil.sensors_battery()
    if battery:
        status = "charging" if battery.power_plugged else "on battery"
        c = "red" if battery.percent < 20 else "green"
        table.add_row(
            "Battery",
            f"[{c}]{bar(battery.percent)} {battery.percent:.0f}%[/{c}]",
            status,
        )

    # Uptime - how long since the last restart
    uptime = timedelta(seconds=int(time.time() - psutil.boot_time()))
    table.add_row("Uptime", str(uptime), "since last restart")

    return table


def main():
    console.print(f"[dim]{platform.system()} {platform.release()} · {platform.node()}[/dim]")
    console.print(build_table())


if __name__ == "__main__":
    main()
