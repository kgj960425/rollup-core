"""
FastAPI 서버 - 서버 자원 모니터링 API
"""
from fastapi import FastAPI
from datetime import datetime
import platform
import psutil

app = FastAPI(
    title="Server Health Check API",
    description="서버 자원 상태를 모니터링하는 API",
    version="1.0.0"
)


@app.get("/v1/api/pingcheck")
async def ping_check():
    """
    서버 자원 상태를 조회하는 엔드포인트
    CPU, 메모리, 디스크 사용량 및 시스템 정보를 반환합니다.
    """
    # CPU 정보
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    cpu_count_logical = psutil.cpu_count(logical=True)
    
    # 메모리 정보
    memory = psutil.virtual_memory()
    memory_info = {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "percent": memory.percent
    }
    
    # 디스크 정보
    disk = psutil.disk_usage('/')
    disk_info = {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent
    }
    
    # 네트워크 정보
    net_io = psutil.net_io_counters()
    network_info = {
        "bytes_sent_mb": round(net_io.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(net_io.bytes_recv / (1024 ** 2), 2),
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv
    }
    
    # 시스템 정보
    system_info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }
    
    # 부팅 시간
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = (datetime.now() - boot_time).total_seconds()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": {
            "uptime_seconds": round(uptime_seconds, 2),
            "boot_time": boot_time.isoformat()
        },
        "cpu": {
            "usage_percent": cpu_percent,
            "cores_physical": cpu_count,
            "cores_logical": cpu_count_logical
        },
        "memory": memory_info,
        "disk": disk_info,
        "network": network_info,
        "system": system_info
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
