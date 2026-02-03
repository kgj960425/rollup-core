"""
FastAPI 서버 - 서버 자원 모니터링 API
"""
from fastapi import FastAPI
from datetime import datetime
import platform
import psutil
import os
import tempfile

app = FastAPI(
    title="Server Health Check API",
    description="서버 자원 상태를 모니터링하는 API",
    version="1.0.0"
)


def detect_environment():
    """
    실행 환경을 감지합니다.
    Vercel, AWS Lambda, 로컬 등을 구분합니다.
    """
    if os.environ.get("VERCEL"):
        return "vercel_serverless"
    elif os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "aws_lambda"
    elif os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    elif platform.system() == "Windows":
        return "local_windows"
    else:
        return "local_linux"


def get_tmp_disk_usage():
    """
    /tmp 디렉토리의 실제 사용 가능한 디스크 정보를 반환합니다.
    Serverless 환경에서 실제 쓸 수 있는 공간입니다.
    """
    tmp_path = tempfile.gettempdir()
    
    try:
        disk = psutil.disk_usage(tmp_path)
        
        # /tmp 내 실제 사용량 계산
        tmp_used = 0
        for dirpath, dirnames, filenames in os.walk(tmp_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    tmp_used += os.path.getsize(fp)
                except (OSError, IOError):
                    pass
        
        return {
            "path": tmp_path,
            "total_mb": round(disk.total / (1024 ** 2), 2),
            "used_mb": round(tmp_used / (1024 ** 2), 2),
            "free_mb": round(disk.free / (1024 ** 2), 2),
            "percent": round((tmp_used / disk.total) * 100, 2) if disk.total > 0 else 0
        }
    except Exception as e:
        return {"error": str(e), "path": tmp_path}


def get_writable_check():
    """
    실제로 파일을 쓸 수 있는지 테스트합니다.
    """
    tmp_path = tempfile.gettempdir()
    test_file = os.path.join(tmp_path, ".write_test")
    
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return {"writable": True, "path": tmp_path}
    except Exception as e:
        return {"writable": False, "path": tmp_path, "error": str(e)}


@app.get("/v1/api/pingcheck")
async def ping_check():
    """
    서버 자원 상태를 조회하는 엔드포인트
    CPU, 메모리, 디스크 사용량 및 시스템 정보를 반환합니다.
    """
    # 환경 감지
    env_type = detect_environment()
    is_serverless = env_type in ["vercel_serverless", "aws_lambda"]
    
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
    
    # 호스트 디스크 정보 (참고용)
    disk = psutil.disk_usage('/')
    host_disk_info = {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
        "note": "호스트 머신 정보 (공유 자원, 직접 사용 불가)" if is_serverless else "로컬 디스크 정보"
    }
    
    # 실제 사용 가능한 /tmp 디스크 정보
    tmp_disk_info = get_tmp_disk_usage()
    
    # 쓰기 테스트
    writable_info = get_writable_check()
    
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
    
    # Vercel 관련 환경변수 수집
    vercel_info = None
    if is_serverless:
        vercel_info = {
            "region": os.environ.get("VERCEL_REGION", "unknown"),
            "env": os.environ.get("VERCEL_ENV", "unknown"),
            "memory_limit_mb": 1024,  # Vercel 기본값
            "tmp_limit_mb": 512,      # Vercel /tmp 제한
        }
    
    response = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "type": env_type,
            "is_serverless": is_serverless
        },
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
        "disk": {
            "usable": tmp_disk_info,
            "host": host_disk_info,
            "writable": writable_info
        },
        "network": network_info,
        "system": system_info
    }
    
    if vercel_info:
        response["serverless_limits"] = vercel_info
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
