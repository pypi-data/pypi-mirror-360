import os
import platform
import subprocess


# 查看当前进程占用多少内存， 返回int 单位MB
def cat_current_pid_mem(logger) -> int:
    try:
        pid = str(os.getpid())
        if platform.system() == "Windows":
            cmd = ["tasklist", "/fi", f"PID eq {pid}", "/fo", "csv", "/nh"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            size = int(int(result.stdout.split('"')[-2].replace(",", "").split(" ")[0]) / 1024)
        else:
            cmd = ["ps", "-p", pid, "-o", "%mem,rss"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            size = int(int(result.stdout.split(" ")[-1].replace("\n", "")) / 1024)
        logger.info(f"子进程:{pid}, 占用{size}Mb")
        return size
    except Exception as e:
        logger.warning(f"cat_current_pid_mem error: {e}")
        return 0
