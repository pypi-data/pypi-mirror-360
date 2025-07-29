import subprocess
import json
import shutil
import time
import argparse
import sys
from typing import Dict, List, Optional, Union, Any, Tuple

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich import box
import psutil
import platform
import shutil

console: Console = Console()

try:
    from . import __version__, __package_name__
except ImportError:
    __version__ = "0"
    __package_name__ = "GPUTOP"


def safe_float(value, default=None):
    """
    Safely convert value to float with fallback to default.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Converted float value or default
    """
    try:
        if value is None or str(value).strip().lower() in ['', 'n/a', 'na', 'null', 'none']:
            return default
        return float(str(value).strip())
    except (ValueError, TypeError):
        return default


def safe_int(value, default=None):
    """
    Safely convert value to int with fallback to default.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Converted int value or default
    """
    try:
        if value is None or str(value).strip().lower() in ['', 'n/a', 'na', 'null', 'none']:
            return default
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def run_cmd(cmd: str) -> Optional[str]:
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return None


def detect_tools() -> Dict[str, bool]:
    return {
        "nvidia": shutil.which("nvidia-smi") is not None,
        "amd": shutil.which("rocm-smi") is not None,
        "intel": shutil.which("intel_gpu_top") is not None,
    }


def get_versions(tools: Dict[str, bool]) -> Dict[str, str]:
    version_info: Dict[str, str] = {
        "tool": f"{__package_name__} {__version__}",
        "driver": "-",
        "runtime": "-"
    }

    if tools["nvidia"]:
        driver_output: Optional[str] = run_cmd("nvidia-smi --query-gpu=driver_version --format=csv,noheader")
        smi_output: Optional[str] = run_cmd("nvidia-smi")
        cuda_version: str = "-"
        if smi_output:
            for line in smi_output.splitlines():
                if "CUDA Version" in line:
                    parts: List[str] = line.split("CUDA Version:")
                    if len(parts) == 2:
                        cuda_version = parts[1].strip().split()[0]
                    break
        version_info["driver"] = f"Driver Version {driver_output}" if driver_output else "-"
        version_info["runtime"] = f"CUDA {cuda_version}"

    elif tools["amd"]:
        amd_output: Optional[str] = run_cmd("amd-smi version --json")
        if amd_output:
            try:
                data: Dict[str, Any] = json.loads(amd_output)[0]
                driver: str = data.get("amdgpu_version", "-")
                rocm: str = data.get("rocm_version", "-")
                version_info["driver"] = f"Driver Version {driver}"
                version_info["runtime"] = f"ROCm {rocm}"
            except Exception:
                version_info["driver"] = "-"
                version_info["runtime"] = "-"
        else:
            version_info["driver"] = "-"
            version_info["runtime"] = "-"

    elif tools["intel"]:
        version_info["driver"] = "Driver Version Unknown"
        version_info["runtime"] = "XPU Runtime"

    return version_info


def create_info_panel(versions: Dict[str, str]) -> Panel:
    table: Table = Table.grid(expand=True)
    table.add_column(justify="left", ratio=1)
    table.add_column(justify="center", ratio=1)
    table.add_column(justify="right", ratio=1)

    table.add_row(
        f"[bold green]{versions['tool']}[/]",
        f"[yellow]{versions['driver']}[/]",
        f"[cyan]{versions['runtime']}[/]"
    )

    return Panel(
        table,
        title="Info",
        box=box.SQUARE,
    )


def parse_nvidia() -> List[Dict[str, Union[str, int, float]]]:
    cmd: str = (
        "nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,"
        "temperature.gpu,power.draw --format=csv,noheader,nounits"
    )
    output: Optional[str] = run_cmd(cmd)
    if not output:
        return []
    rows: List[Dict[str, Union[str, int, float]]] = []
    for line in output.splitlines():
        parts: List[str] = [p.strip() for p in line.split(",")]
        if len(parts) >= 6:
            rows.append({
                "name": parts[0],
                "mem_used": safe_int(parts[1], 0),
                "mem_total": safe_int(parts[2], 0),
                "gpu_util": safe_float(parts[3], "N/A"),
                "temp": safe_float(parts[4], "N/A"),
                "power": safe_float(parts[5], "N/A")
            })
    return rows


def parse_amd() -> List[Dict[str, Union[str, int, float]]]:
    cmd: str = "rocm-smi --showproductname --showuse --showtemp --showpower --showmeminfo vram --json"
    output: Optional[str] = run_cmd(cmd)
    if not output:
        return []
    try:
        data: Dict[str, Any] = json.loads(output)
        rows: List[Dict[str, Union[str, int, float]]] = []
        for card, info in data.items():
            rows.append({
                "name": info.get("Card Series", "Unknown"),
                "gpu_util": safe_float(info.get("GPU use (%)", "0"), "N/A"),
                "temp": safe_float(info.get("Temperature (Sensor edge) (C)", "0"), "N/A"),
                "power": safe_float(info.get("Current Socket Graphics Package Power (W)", "0"), "N/A"),
                "mem_used": safe_int(info.get("VRAM Total Used Memory (B)", 0), 0) // (1024 ** 2),
                "mem_total": safe_int(info.get("VRAM Total Memory (B)", 0), 0) // (1024 ** 2)
            })
        return rows
    except Exception:
        return []


def parse_intel() -> List[Dict[str, Union[str, int, float]]]:
    cmd: str = "intel_gpu_top -J -s 500 -d 1"
    output: Optional[str] = run_cmd(cmd)
    if not output:
        return []
    try:
        data: Dict[str, Any] = json.loads(output)
        render_busy: float = data["engines"].get("Render/3D/0", {}).get("busy", 0)
        return [{
            "name": "Intel GPU",
            "gpu_util": safe_int(render_busy, 0),
            "temp": safe_int(data.get("temperature", 0), 0),
            "power": safe_float(data.get("power", 0), 0.0),
            "mem_used": 0,
            "mem_total": 0
        }]
    except Exception:
        return []


def get_nvidia_processes() -> List[Dict[str, str]]:
    cmd: str = "nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits"
    output: Optional[str] = run_cmd(cmd)
    if not output:
        return []
    processes: List[Dict[str, str]] = []
    for line in output.splitlines():
        parts: List[str] = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        pid, name, mem = parts
        processes.append({
            "pid": pid,
            "name": name,
            "mem": str(safe_int(mem, 0))
        })
    return processes


def get_amd_processes() -> List[Dict[str, str]]:
    cmd: str = "rocm-smi --showpids --csv"
    output: Optional[str] = run_cmd(cmd)
    procs: List[Dict[str, str]] = []

    if not output:
        return procs

    lines: List[str] = output.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('"PID'):
            try:
                key, val = line.split(",", 1)
                pid: str = key.replace("PID", "").strip().strip('"')
                val = val.strip().strip('"')
                parts: List[str] = [p.strip() for p in val.split(",")]
                if len(parts) >= 3:
                    name: str = parts[0]
                    mem_bytes: int = safe_int(parts[2], 0)
                    mem_mib: int = mem_bytes // (1024 ** 2)
                    procs.append({
                        "pid": pid,
                        "name": name,
                        "mem": str(mem_mib)
                    })
            except Exception:
                continue
    return procs


def create_table(
        gpu_data: List[Dict[str, Union[str, int, float]]],
        gpu_processes: List[Dict[str, str]]
) -> Tuple[Table, Panel, Panel]:
    title: Text = Text("")

    table: Table = Table(title=title, box=box.SQUARE, expand=True)
    table.add_column("GPU")
    table.add_column("Usage %")
    table.add_column("Temp °C")
    table.add_column("Power W")
    table.add_column("Memory Used")

    for gpu in gpu_data:
        mem_str: str = f"{gpu['mem_used']} / {gpu['mem_total']} MiB" if gpu['mem_total'] else "-"
        table.add_row(
            str(gpu["name"]),
            str(gpu["gpu_util"]),
            str(gpu["temp"]),
            f"{gpu['power']:.1f}" if isinstance(gpu['power'], float) else gpu['power'],
            mem_str
        )

    cpu: float = psutil.cpu_percent()
    ram: psutil._pslinux.svmem = psutil.virtual_memory()
    cpu_count: int = psutil.cpu_count(logical=True)
    kernel_version: str = platform.release()
    os_name: str = platform.system()
    disk: shutil.disk_usage = shutil.disk_usage("/")
    disk_total_gb: int = disk.total // (1024 ** 3)
    disk_used_gb: int = disk_total_gb -  disk.free // (1024 ** 3)


    sys_table = Table.grid(expand=True)

    # Добавляем 3 колонки
    sys_table.add_column(justify="left", ratio=1)
    sys_table.add_column(justify="center", ratio=1)
    sys_table.add_column(justify="right", ratio=1)

    # Первая строка: OS, CPU Cores, RAM Used
    sys_table.add_row(
        f"[cyan]OS:[/] {os_name}",
        f"[cyan]CPU Cores:[/] {cpu_count}",
        f"[cyan]RAM Used:[/] {ram.used // (1024 ** 2)} MiB / {ram.total // (1024 ** 2)} MiB"
    )

    # Вторая строка: Kernel, CPU Load, Disk Used
    sys_table.add_row(
        f"[cyan]Kernel:[/] {kernel_version}",
        f"[cyan]CPU Load:[/] {cpu:.1f}%",
        f"[cyan]Disk Used:[/] {disk_used_gb} GB / {disk_total_gb} GB"
    )

    info_panel = Panel(
        sys_table,
        title="",
        box=box.SQUARE,
    )

    process_table: Table = Table(box=box.SIMPLE, expand=True)
    process_table.add_column("PID", style="cyan")
    process_table.add_column("Name", style="magenta")
    process_table.add_column("GPU Mem (MiB)", justify="right")

    if gpu_processes:
        for proc in gpu_processes:
            process_table.add_row(proc["pid"], proc["name"], proc["mem"])
    else:
        process_table.add_row("-", "No GPU processes", "-")

    process_panel: Panel = Panel(
        process_table,
        title="",
        box=box.SQUARE,
        padding=(0, 0)
    )

    return table, info_panel, process_panel

def run_monitor() -> None:
    tools: Dict[str, bool] = detect_tools()
    versions: Dict[str, str] = get_versions(tools)

    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            gpus: List[Dict[str, Union[str, int, float]]] = []
            if tools["nvidia"]:
                gpus.extend(parse_nvidia())
            if tools["amd"]:
                gpus.extend(parse_amd())
            if tools["intel"]:
                gpus.extend(parse_intel())

            processes: List[Dict[str, str]] = []
            if tools["nvidia"]:
                processes += get_nvidia_processes()
            if tools["amd"]:
                processes += get_amd_processes()
            if tools["intel"]:
                processes += []

            table, info, proc_table = create_table(gpus, processes)
            layout: Table = Table.grid(expand=True)
            layout.add_row(create_info_panel(versions))
            layout.add_row(table)
            layout.add_row(info)
            layout.add_row(proc_table)

            live.update(layout)
            time.sleep(0.5)


def parse_args() -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='gputop',
        description='Real-time GPU monitoring tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gputop              # Start GPU monitoring
  gputop --help       # Show help
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'{__package_name__} {__version__}',
        help='Show program version'
    )

    return parser.parse_args()


def main() -> None:
    parse_args()

    try:
        run_monitor()
    except KeyboardInterrupt:
        console.clear()
        sys.exit(0)


if __name__ == "__main__":
    main()
