"""OSLab CAP · Kumar Subodh · Operating Systems Laboratory."""
from __future__ import annotations

import posixpath
import os
from collections import deque

from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
PUBLIC_DEMO = os.getenv("OSLAB_DEMO", "0").lower() in {"1", "true", "yes"}
MONITOR_CLIENT_ORIGIN = "https://os-lab-cap.onrender.com"


def body():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ValueError("Send a JSON object with the simulator inputs.")
    return value


def ints(value, label, minimum=0):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list of numbers.")
    try:
        result = [int(v) for v in value]
    except (TypeError, ValueError):
        raise ValueError(f"{label} must contain whole numbers.") from None
    if any(v < minimum for v in result):
        raise ValueError(f"{label} values must be at least {minimum}.")
    return result


def processes(value):
    if not isinstance(value, list) or not value or len(value) > 100:
        raise ValueError("Enter between 1 and 100 processes.")
    result, ids = [], set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("Each process must be an object.")
        pid = str(row.get("id", "")).strip()[:32]
        if not pid or pid in ids:
            raise ValueError("Process IDs must be present and unique.")
        ids.add(pid)
        try:
            arrival, burst = int(row.get("arrival", 0)), int(row.get("burst", 0))
            priority = int(row.get("priority", 0))
        except (TypeError, ValueError):
            raise ValueError(f"Process {pid} has a non-numeric value.") from None
        if arrival < 0 or burst <= 0:
            raise ValueError(f"Process {pid}: arrival must be ≥ 0 and burst must be > 0.")
        result.append({"id": pid, "arrival": arrival, "burst": burst, "priority": priority, "remaining": burst})
    return result


def cpu_schedule(data):
    items = processes(data.get("processes"))
    algorithm = str(data.get("algorithm", "fcfs")).lower()
    if algorithm not in {"fcfs", "sjf", "rr", "priority"}:
        raise ValueError("Choose FCFS, SJF, Round Robin, or Priority.")
    try:
        quantum = int(data.get("quantum", 2))
    except (TypeError, ValueError):
        raise ValueError("Time quantum must be a positive whole number.") from None
    if algorithm == "rr" and quantum <= 0:
        raise ValueError("Time quantum must be a positive whole number.")
    time, complete, gantt, ready = 0, 0, [], deque()
    pending = sorted(items, key=lambda p: (p["arrival"], p["id"]))
    rr = algorithm == "rr"
    while complete < len(items):
        while pending and pending[0]["arrival"] <= time:
            ready.append(pending.pop(0))
        if not ready:
            next_time = pending[0]["arrival"]
            gantt.append({"id": "Idle", "start": time, "end": next_time})
            time = next_time
            continue
        if algorithm == "sjf":
            job = min(ready, key=lambda p: (p["burst"], p["arrival"], p["id"]))
            ready.remove(job)
        elif algorithm == "priority":
            job = min(ready, key=lambda p: (p["priority"], p["arrival"], p["id"]))
            ready.remove(job)
        else:
            job = ready.popleft()
        duration = min(job["remaining"], quantum) if rr else job["remaining"]
        start = time
        time += duration
        job["remaining"] -= duration
        if gantt and gantt[-1]["id"] == job["id"] and gantt[-1]["end"] == start:
            gantt[-1]["end"] = time
        else:
            gantt.append({"id": job["id"], "start": start, "end": time})
        while pending and pending[0]["arrival"] <= time:
            ready.append(pending.pop(0))
        if job["remaining"]:
            ready.append(job)
        else:
            job["completion"] = time
            complete += 1
    rows = []
    for p in items:
        turnaround = p["completion"] - p["arrival"]
        rows.append({"id": p["id"], "arrival": p["arrival"], "burst": p["burst"], "priority": p["priority"], "completion": p["completion"], "waiting": turnaround - p["burst"], "turnaround": turnaround})
    return {"algorithm": algorithm, "gantt": gantt, "processes": rows,
            "averageWaiting": round(sum(p["waiting"] for p in rows) / len(rows), 2),
            "averageTurnaround": round(sum(p["turnaround"] for p in rows) / len(rows), 2), "totalTime": time}


def memory_sim(data):
    mode = data.get("mode", "allocation")
    if mode == "paging":
        size = int(data.get("pageSize", 0))
        if size <= 0: raise ValueError("Page size must be positive.")
        ps = data.get("processes", [])
        rows = [{"id": str(p["id"]), "size": int(p["size"]), "pages": (int(p["size"])+size-1)//size,
                 "fragmentation": ((int(p["size"])+size-1)//size)*size-int(p["size"])} for p in ps]
        return {"mode": mode, "pageSize": size, "processes": rows, "totalPages": sum(x["pages"] for x in rows), "fragmentation": sum(x["fragmentation"] for x in rows)}
    if mode == "segmentation":
        capacity = int(data.get("totalMemory", 0))
        if capacity <= 0: raise ValueError("Memory capacity must be positive.")
        cursor, rows = 0, []
        for segment in data.get("segments", []):
            size = int(segment["size"])
            if size <= 0: raise ValueError("Segment sizes must be positive.")
            rows.append({"process": str(segment["process"]), "name": str(segment["name"]), "base": cursor, "limit": size, "allocated": cursor+size <= capacity})
            cursor += size
        return {"mode": mode, "capacity": capacity, "used": min(cursor, capacity), "free": max(0, capacity-cursor), "segments": rows}
    blocks = ints(data.get("blocks"), "Memory blocks", 1)
    ps = data.get("processes", [])
    strategy = data.get("strategy", "first")
    free = list(blocks)
    rows = []
    for process in ps:
        size = int(process["size"])
        if size <= 0: raise ValueError("Process sizes must be positive.")
        candidates = [i for i, amount in enumerate(free) if amount >= size]
        index = (min(candidates, key=lambda i: free[i]) if strategy == "best" else
                 max(candidates, key=lambda i: free[i]) if strategy == "worst" else
                 candidates[0] if candidates else None)
        if index is None:
            rows.append({"id": str(process["id"]), "size": size, "block": None, "fragmentation": 0})
        else:
            waste = free[index] - size
            free[index] = waste
            rows.append({"id": str(process["id"]), "size": size, "block": index+1, "fragmentation": waste})
    return {"mode": mode, "strategy": strategy, "blocks": blocks, "freeBlocks": free, "processes": rows,
            "allocated": sum(x["block"] is not None for x in rows), "freeMemory": sum(free), "largestFreeBlock": max(free, default=0)}


def banker(data):
    available = ints(data.get("available"), "Available resources")
    allocations, needs = data.get("allocation", []), data.get("need", [])
    if not allocations or len(allocations) != len(needs): raise ValueError("Allocation and need matrices must have the same non-zero number of rows.")
    n = len(available)
    if any(len(row) != n for row in allocations+needs): raise ValueError("Every resource vector must match the available-resource width.")
    work, finish, sequence = list(available), [False]*len(needs), []
    for _ in needs:
        index = next((i for i,row in enumerate(needs) if not finish[i] and all(row[j] <= work[j] for j in range(n))), None)
        if index is None: break
        work = [work[j]+allocations[index][j] for j in range(n)]
        finish[index] = True
        sequence.append(f"P{index}")
    return {"safe": len(sequence) == len(needs), "sequence": sequence,
            "processes": [{"id": f"P{i}", "allocation": allocations[i], "need": needs[i], "canFinish": finish[i]} for i in range(len(needs))]}


def disk_schedule(data):
    requests = ints(data.get("requests"), "Disk requests")
    head, maximum = int(data.get("head", 0)), int(data.get("maxTrack", 199))
    algorithm, direction = data.get("algorithm", "fcfs"), data.get("direction", "right")
    if maximum < 1 or head < 0 or head > maximum or any(r > maximum for r in requests): raise ValueError("Head and requests must be within the disk range.")
    lo, hi = sorted((r for r in requests if r < head), reverse=True), sorted(r for r in requests if r >= head)
    if algorithm == "sstf":
        pending, order, current = list(requests), [], head
        while pending:
            nxt = min(pending, key=lambda r: abs(r-current)); pending.remove(nxt); order.append(nxt); current = nxt
    elif algorithm in {"scan", "cscan", "look"}:
        if direction == "right":
            order = hi + ([maximum] if algorithm == "scan" and lo else []) + (lo[::-1] if algorithm == "scan" else ([0]+lo[::-1] if algorithm == "cscan" and lo else lo[::-1]))
            if algorithm == "cscan" and lo: order = hi+[maximum,0]+lo[::-1]
        else:
            order = lo + ([0] if algorithm == "scan" and hi else []) + (hi[::-1] if algorithm == "scan" else ([maximum]+hi[::-1] if algorithm == "cscan" and hi else hi[::-1]))
            if algorithm == "cscan" and hi: order = lo+[0,maximum]+hi[::-1]
    elif algorithm == "fcfs": order = requests
    else: raise ValueError("Choose FCFS, SSTF, SCAN, C-SCAN, or LOOK.")
    path = [head] + order
    travel = sum(abs(path[i]-path[i-1]) for i in range(1, len(path)))
    return {"algorithm": algorithm, "path": path, "travel": travel, "average": round(travel/len(requests), 2)}


def page_replacement(data):
    refs = ints(data.get("references"), "Page references")
    count, algorithm = int(data.get("frames", 3)), data.get("algorithm", "fifo")
    if count < 1 or count > 32: raise ValueError("Frame count must be between 1 and 32.")
    if algorithm not in {"fifo", "lru", "optimal"}: raise ValueError("Choose FIFO, LRU, or Optimal.")
    frames, last, pointer, faults, rows = [None]*count, {}, 0, 0, []
    for step, page in enumerate(refs):
        hit = page in frames
        if not hit:
            faults += 1
            try: slot = frames.index(None)
            except ValueError:
                if algorithm == "fifo": slot, pointer = pointer, (pointer+1) % count
                elif algorithm == "lru": slot = min(range(count), key=lambda i: last[frames[i]])
                else:
                    future = [refs.index(frames[i], step+1) if frames[i] in refs[step+1:] else float("inf") for i in range(count)]
                    slot = max(range(count), key=lambda i: future[i])
            frames[slot] = page
        last[page] = step
        rows.append({"step": step+1, "page": page, "hit": hit, "frames": list(frames)})
    return {"algorithm": algorithm, "faults": faults, "hits": len(refs)-faults, "hitRatio": round((len(refs)-faults)/len(refs)*100, 1), "steps": rows}


@app.get("/")
def home(): return render_template("index.html", demo=PUBLIC_DEMO)


@app.post("/api/simulate/cpu")
def api_cpu(): return jsonify(cpu_schedule(body()))


@app.post("/api/simulate/memory")
def api_memory(): return jsonify(memory_sim(body()))


@app.post("/api/simulate/deadlock")
def api_deadlock(): return jsonify(banker(body()))


@app.post("/api/simulate/disk")
def api_disk(): return jsonify(disk_schedule(body()))


@app.post("/api/simulate/pages")
def api_pages(): return jsonify(page_replacement(body()))


@app.post("/api/simulate/translation")
def api_translation():
    data = body(); table = {int(row["page"]): int(row["frame"]) for row in data.get("table", [])}
    refs = ints(data.get("references"), "Virtual page references")
    size = int(data.get("tlbSize", 3))
    if size < 1: raise ValueError("TLB size must be positive.")
    tlb, rows, misses, faults = [], [], 0, 0
    for step, page in enumerate(refs, 1):
        frame = table.get(page)
        hit = frame is not None and page in tlb
        if frame is None: faults += 1
        elif not hit:
            misses += 1; tlb = [page] + [p for p in tlb if p != page]; tlb = tlb[:size]
        else: tlb = [page] + [p for p in tlb if p != page]
        rows.append({"step": step, "page": page, "frame": frame, "status": "Page fault" if frame is None else ("TLB hit" if hit else "Page-table lookup"), "tlb": list(tlb)})
    return jsonify({"steps": rows, "tlbMisses": misses, "pageFaults": faults, "hitRatio": round(max(0,(len(refs)-misses-faults)/len(refs)*100),1)})


@app.post("/api/simulate/synchronization")
def api_sync():
    data = body(); scenario = data.get("scenario", "producer"); capacity = max(2, min(10, int(data.get("capacity", 4))))
    scenarios = {
        "producer": {"name":"Producer–Consumer", "summary":"A mutex protects the buffer; counting semaphores track empty and full slots.", "resources":[{"name":"empty","value":capacity,"role":"Free buffer slots"},{"name":"full","value":0,"role":"Occupied slots"},{"name":"mutex","value":1,"role":"Exclusive access"}], "steps":["Producer waits while empty = 0","Producer acquires mutex and inserts an item","empty decreases; full increases","Consumer waits while full = 0","Consumer removes an item and signals empty"]},
        "readers": {"name":"Readers–Writers", "summary":"Concurrent readers share access; writers enter one at a time after active readers leave.", "resources":[{"name":"readers","value":2,"role":"Concurrent read locks"},{"name":"writer","value":0,"role":"Exclusive write lock"}], "steps":["Reader 1 acquires a shared lock","Reader 2 joins safely","Writer waits while readers are active","Readers release their locks","Writer acquires exclusive access"]},
        "dining": {"name":"Dining Philosophers", "summary":"A waiter grants both forks together, preventing circular wait and deadlock.", "resources":[{"name":"philosophers","value":5,"role":"Competing tasks"},{"name":"forks","value":5,"role":"Shared resources"}], "steps":["Philosopher requests both neighboring forks","Waiter checks that both are free","Both forks are granted atomically","Philosopher eats, then releases both forks","Other waiting philosophers can proceed"]}}
    if scenario not in scenarios: raise ValueError("Choose Producer–Consumer, Readers–Writers, or Dining Philosophers.")
    return jsonify(scenarios[scenario] | {"capacity":capacity})


@app.post("/api/shell")
def api_shell():
    data = body(); command = str(data.get("command", "")).strip()
    files, dirs, cwd = data.get("files", {}), set(data.get("dirs", ["/", "/home", "/home/student", "/home/student/docs", "/home/student/projects"])), str(data.get("cwd", "/home/student"))
    if len(command) > 500 or not isinstance(files, dict) or len(files) > 100: raise ValueError("Virtual shell input exceeds its size limit.")
    words = command.split(); out = ""
    if not words: pass
    elif words[0] == "help": out = "Commands: help, pwd, ls, cd, mkdir, touch, write, cat, rm, clear. Virtual sandbox only."
    elif words[0] == "pwd": out = cwd
    elif words[0] == "ls": out = "  ".join(sorted([p.rsplit("/",1)[-1] for p in files if p.startswith(cwd.rstrip("/")+"/")] + [p.rsplit("/",1)[-1]+"/" for p in dirs if p.rpartition("/")[0] == cwd])) or "(empty directory)"
    elif words[0] == "cd":
        target = posixpath.normpath(posixpath.join(cwd, words[1])) if len(words)>1 else "/home/student"
        if target in dirs: cwd = target
        else: out = f"cd: no such directory: {target}"
    elif words[0] == "mkdir" and len(words)>1: dirs.add(posixpath.normpath(posixpath.join(cwd, words[-1])))
    elif words[0] in {"touch","write"} and len(words)>1:
        key=posixpath.normpath(posixpath.join(cwd, words[1])); files[key] = " ".join(words[2:]) if words[0]=="write" else files.get(key, "")
    elif words[0] == "cat": out = files.get(posixpath.normpath(posixpath.join(cwd, words[1] if len(words)>1 else "")), "cat: file not found")
    elif words[0] == "rm": out = "" if files.pop(posixpath.normpath(posixpath.join(cwd, words[-1])), None) is not None else "rm: file not found"
    elif words[0] == "clear": out = "__CLEAR__"
    else: out = "Command unavailable in the safe virtual shell. Type help."
    return jsonify({"output":out,"cwd":cwd,"files":files,"dirs":sorted(dirs)})


@app.route("/api/monitor", methods=["GET", "OPTIONS"])
def api_monitor():
    # The deployed site may read this one endpoint from the visitor's own
    # loopback service. Never grant cross-origin access to any other origin.
    origin = request.headers.get("Origin")
    if origin and origin != MONITOR_CLIENT_ORIGIN:
        return jsonify(error="This origin is not allowed to read local monitoring data."), 403
    if request.method == "OPTIONS": return "", 204
    if PUBLIC_DEMO: return jsonify(error="Live host monitoring is only available when running locally."), 403
    try:
        import psutil
        rows = [{"pid":p.info["pid"],"name":p.info["name"] or "Unknown","cpu":round(p.info.get("cpu_percent") or 0,1),"memory":round(p.info.get("memory_percent") or 0,2)} for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent"],ad_value=0)]
        rows.sort(key=lambda p:(p["memory"],p["cpu"]),reverse=True)
        return jsonify({"cpu":psutil.cpu_percent(interval=.15),"memory":psutil.virtual_memory()._asdict(),"processes":rows[:12]})
    except ImportError: return jsonify(error="Install the requirements to enable the live monitor."), 503


@app.errorhandler(ValueError)
def bad_input(error): return jsonify(error=str(error)), 400


@app.errorhandler(413)
def request_too_large(_): return jsonify(error="Request payload exceeds 1 MB."), 413


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' http://127.0.0.1:5000; frame-ancestors 'none'; base-uri 'none'"
    if request.path == "/api/monitor" and request.headers.get("Origin") == MONITOR_CLIENT_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = MONITOR_CLIENT_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        response.headers["Vary"] = "Origin"
    if request.path.startswith("/api/"): response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
