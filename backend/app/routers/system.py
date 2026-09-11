from fastapi import APIRouter
import psutil
import shutil
import subprocess

router = APIRouter()

# Initial call to seed cpu_percent measurement baseline
psutil.cpu_percent(interval=None)


def query_gpu_info() -> dict:
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return {
            "available": False,
            "name": "N/A",
            "percent": 0.0,
            "memory_used_gb": 0.0,
            "memory_total_gb": 0.0,
            "memory_percent": 0.0,
        }
    try:
        res = subprocess.run(
            [
                nvidia_smi,
                "--query-gpu=utilization.gpu,memory.used,memory.total,name",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0 and res.stdout.strip():
            lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
            if lines:
                parts = [p.strip() for p in lines[0].split(",")]
                try:
                    gpu_util = float(parts[0]) if len(parts) > 0 else 0.0
                except (ValueError, TypeError):
                    gpu_util = 0.0

                try:
                    mem_used = float(parts[1]) if len(parts) > 1 else 0.0
                except (ValueError, TypeError):
                    mem_used = 0.0

                try:
                    mem_total = float(parts[2]) if len(parts) > 2 else 0.0
                except (ValueError, TypeError):
                    mem_total = 0.0

                name = parts[3] if len(parts) > 3 else "GPU"
                mem_pct = round((mem_used / mem_total) * 100, 1) if mem_total > 0 else 0.0

                return {
                    "available": True,
                    "name": name,
                    "percent": round(gpu_util, 1),
                    "memory_used_mb": round(mem_used, 1),
                    "memory_total_mb": round(mem_total, 1),
                    "memory_used_gb": round(mem_used / 1024, 1),
                    "memory_total_gb": round(mem_total / 1024, 1),
                    "memory_percent": mem_pct,
                }
    except Exception:
        pass

    return {
        "available": False,
        "name": "N/A",
        "percent": 0.0,
        "memory_used_gb": 0.0,
        "memory_total_gb": 0.0,
        "memory_percent": 0.0,
    }


@router.get("/system/resources")
@router.get("/system/metrics")
def get_system_resources():
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    ram_total_gb = round(mem.total / (1024**3), 1)
    ram_used_gb = round(mem.used / (1024**3), 1)
    ram_percent = round(mem.percent, 1)

    gpu_info = query_gpu_info()

    return {
        "cpu": {
            "percent": round(cpu_pct, 1),
            "cores": psutil.cpu_count(logical=True) or 1,
        },
        "ram": {
            "used_gb": ram_used_gb,
            "total_gb": ram_total_gb,
            "percent": ram_percent,
        },
        "gpu": gpu_info,
    }
