from fastapi import FastAPI, Query
from subprocess import Popen, PIPE
from typing import Dict
from threading import Thread
from pathlib import Path
import time
import json
import os
import signal
import psutil

app = FastAPI(title="kubetap API")

TUNNEL_FILE = Path.home() / ".kubetap/tunnels.json"
TUNNEL_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_tunnels():
    if TUNNEL_FILE.exists():
        try:
            with open(TUNNEL_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tunnels(tunnels):
    with open(TUNNEL_FILE, "w") as f:
        json.dump(tunnels, f, indent=2)

def tunnel_watcher():
    while True:
        tunnels = load_tunnels()
        changed = False
        for cluster, info in list(tunnels.items()):
            pid = info.get("pid")
            if not pid or not psutil.pid_exists(pid):
                print(f"[kubetap] Tunnel '{cluster}' died or missing")
                tunnels.pop(cluster)
                changed = True
            else:
                try:
                    result = Popen(["kubectl", "get", "nodes", "--context", cluster], stdout=PIPE, stderr=PIPE)
                    stdout, stderr = result.communicate(timeout=5)
                    if result.returncode != 0:
                        print(f"[kubetap] kubectl check failed for {cluster}: {stderr.decode().strip()}")
                except Exception as e:
                    print(f"[kubetap] kubectl check error for {cluster}: {str(e)}")

        if changed:
            save_tunnels(tunnels)
        time.sleep(10)

Thread(target=tunnel_watcher, daemon=True).start()

@app.post("/start")
def start_tunnel(cluster: str = Query(...)):
    tunnels = load_tunnels()
    if cluster in tunnels and psutil.pid_exists(tunnels[cluster]["pid"]):
        return {"status": "already running", "cluster": cluster}

    cmd = ["kubetap", "start", cluster]

    try:
        proc = Popen(cmd)
        tunnels[cluster] = {
            "pid": proc.pid,
            "cluster": cluster,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        save_tunnels(tunnels)
        return {"status": "started", "cluster": cluster}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/stop")
def stop_tunnel(cluster: str = Query(...)):
    tunnels = load_tunnels()
    info = tunnels.get(cluster)

    if not info:
        return {"status": "not running"}

    pid = info.get("pid")
    try:
        if pid and psutil.pid_exists(pid):
            os.kill(pid, signal.SIGTERM)
        tunnels.pop(cluster, None)
        save_tunnels(tunnels)
        return {"status": "stopped", "cluster": cluster}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/status")
def status():
    tunnels = load_tunnels()
    alive = {k: v for k, v in tunnels.items() if psutil.pid_exists(v.get("pid", -1))}
    return {"running": list(alive.keys())}

def run_server():
    import uvicorn
    uvicorn.run("kubetap.server:app", host="127.0.0.1", port=8787, reload=True)
