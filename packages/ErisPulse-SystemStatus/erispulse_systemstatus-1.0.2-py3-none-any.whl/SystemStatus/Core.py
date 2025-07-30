import platform
import subprocess
import os
import psutil
from importlib.metadata import version

class Main:
    def __init__(self, sdk):
        self.sdk = sdk
        self.logger = self.sdk.logger
        
    def get(self):
        """获取系统信息并返回包含版本信息的字典"""
        system_name = platform.system()
        version_info = "Unknown"
        
        # 获取系统版本信息
        if system_name == "Windows":
            try:
                major = subprocess.run(
                    ["powershell", "-Command", "[System.Environment]::OSVersion.Version.Major"],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                nt_ver = "NT " + major
                try: 
                    nt_ver = subprocess.run(
                        ["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion", "/v", "CurrentVersion"],
                        capture_output=True, text=True, check=True
                    ).stdout.split()[-1]
                except: 
                    try: 
                        nt_ver = subprocess.run(
                            ["cmd", "/c", "ver"],
                            capture_output=True, text=True, check=True
                        ).stdout.strip().split()[-1]
                    except: 
                        pass
                version_info = f"Windows {major} ({nt_ver})"
            except:
                version_info = "Windows (Unknown Version)"
                
        elif system_name == "Linux":
            try:
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release") as f:
                        os_release = dict(
                            line.strip().split("=")
                            for line in f if "=" in line and not line.startswith("#")
                        )
                    name = os_release.get("NAME", "").strip('"')
                    ver = os_release.get("VERSION_ID", "").strip('"')
                    
                    if "com.termux" in platform.release():
                        try:
                            android_ver = subprocess.run(
                                ["getprop", "ro.build.version.release"],
                                capture_output=True, text=True, check=True
                            ).stdout.strip()
                            version_info = f"Termux {android_ver} (Android {android_ver})"
                        except:
                            version_info = "Termux (Unknown Version)"
                    
                    if "ubuntu" in name.lower():
                        try:
                            code = subprocess.run(
                                ["lsb_release", "-cs"],
                                capture_output=True, text=True, check=True
                            ).stdout.strip()
                            version_info = f"Ubuntu {ver} ({code})"
                        except:
                            version_info = f"Ubuntu {ver}"
                    elif "debian" in name.lower():
                        version_info = f"Debian {ver}"
                    elif "centos" in name.lower():
                        version_info = f"CentOS {ver}"
                    elif "fedora" in name.lower():
                        version_info = f"Fedora {ver}"
                    elif "arch" in name.lower():
                        version_info = f"Arch Linux {ver}"
                    else:
                        version_info = f"{name} {ver}" if ver else name
                else:
                    try:
                        uname = subprocess.run(
                            ["uname", "-a"],
                            capture_output=True, text=True, check=True
                        ).stdout.strip()
                        version_info = f"Linux ({uname})"
                    except:
                        version_info = "Linux (Unknown Distribution)"
            except:
                version_info = "Linux (Unknown)"
                
        elif system_name == "Darwin":
            try:
                ver = subprocess.run(
                    ["sw_vers", "-productVersion"],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                version_info = f"MacOS {ver}"
            except:
                version_info = "MacOS (Unknown)"
                
        elif system_name == "Android":
            try:
                ver = subprocess.run(
                    ["getprop", "ro.build.version.release"],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                version_info = f"Android {ver}"
            except:
                version_info = "Android (Unknown)"
                
        elif system_name == "ChromeOS":
            try:
                if os.path.exists("/etc/lsb-release"):
                    lsb = subprocess.run(
                        ["cat", "/etc/lsb-release"],
                        capture_output=True, text=True, check=True
                    ).stdout
                    version_info = "FydeOS" if "FydeOS" in lsb else "ChromeOS"
                else:
                    version_info = "ChromeOS (Unknown)"
            except:
                version_info = "ChromeOS (Unknown)"

        # 获取系统内存信息
        try:
            memory = psutil.virtual_memory()
            memory_total = int(memory.total / (1024 * 1024))
            memory_used = int((memory.total - memory.available) / (1024 * 1024))
            memory_usage = round((memory_used / memory_total) * 100, 2) if memory_total > 0 else 0.0
            memory_usage_str = f"{memory_usage}%" if memory_usage is not None else "无法获取"
        except:
            memory_usage_str = "无法获取"

        # 获取CPU信息
        try:
            cpu_usage = psutil.cpu_percent(interval=1)  # 已经是百分比形式
            cpu_usage_str = f"{round(cpu_usage, 2)}%" if cpu_usage is not None else "无法获取"
        except:
            cpu_usage_str = "无法获取"

        # 获取硬盘信息
        try:
            disk = psutil.disk_usage('/')
            disk_total = int(disk.total / (1024 ** 3))
            disk_used = int(disk.used / (1024 ** 3))
            disk_usage = round((disk_used / disk_total) * 100, 2) if disk_total > 0 else 0.0
            disk_usage_str = f"{disk_usage}%" if disk_usage is not None else "无法获取"
        except:
            disk_usage_str = "无法获取"

        return {
            "system": {
                "type": system_name,
                "version": version_info,
            },
            "memory": {
                "total": memory_total,
                "used": memory_used,
                "usage": memory_usage_str  # "xx.xx%"格式的字符串
            },
            "cpu": {
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "usage": cpu_usage_str  # "xx.xx%"格式的字符串
            },
            "disk": {
                "total": f"{disk_total}GB",
                "used": f"{disk_used}GB",
                "usage": disk_usage_str  # "xx.xx%"格式的字符串
            },
            "env": {
                "erispulse": version('ErisPulse'),
                "python": platform.python_version()
            }
        }
