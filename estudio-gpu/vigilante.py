#!/usr/bin/env python3
"""Idle watchdog for the GPU pod: stops the pod after N minutes with no ComfyUI work,
so a forgotten pod never keeps billing. Uses RunPod's runpodctl (present inside RunPod
pods together with $RUNPOD_POD_ID). If it is not available it logs a loud warning."""
import argparse, json, os, shutil, subprocess, time, urllib.request

def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1:8188{path}", timeout=10) as r:
        return json.loads(r.read())

ap = argparse.ArgumentParser()
ap.add_argument("--minutos", type=int, default=20)
a = ap.parse_args()
last_activity, last_seen = time.time(), None
while True:
    time.sleep(60)
    try:
        q = get("/queue")
        busy = bool(q.get("queue_running") or q.get("queue_pending"))
        hist = len(get("/history?max_items=500"))
    except Exception as e:
        print(f"{time.ctime()} ComfyUI no responde ({e}); cuenta como inactivo", flush=True)
        busy, hist = False, last_seen
    if busy or hist != last_seen:
        last_activity, last_seen = time.time(), hist
    idle = (time.time() - last_activity) / 60
    print(f"{time.ctime()} ocupado={busy} inactivo={idle:.0f} min", flush=True)
    if idle >= a.minutos:
        pod = os.environ.get("RUNPOD_POD_ID")
        if shutil.which("runpodctl") and pod:
            print(f"{time.ctime()} {a.minutos} min sin trabajo: deteniendo el pod {pod}", flush=True)
            subprocess.run(["runpodctl", "stop", "pod", pod])
        else:
            print("AVISO: no encuentro runpodctl/RUNPOD_POD_ID. ¡Detén el pod a mano en runpod.io!", flush=True)
        break
