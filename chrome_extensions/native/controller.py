import subprocess, os, signal, psutil

PROC_FILE = "main.pid"

def start():
    proc = subprocess.Popen(["python", "main.py"])
    with open(PROC_FILE, "w") as f:
        f.write(str(proc.pid))

def stop():
    if os.path.exists(PROC_FILE):
        with open(PROC_FILE) as f:
            pid = int(f.read())
        if psutil.pid_exists(pid):
            os.kill(pid, signal.SIGTERM)
        os.remove(PROC_FILE)