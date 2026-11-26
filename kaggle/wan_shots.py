"""Run on a Kaggle notebook (GPU T4 x2). Animates each keyframe with Wan 2.2 TI2V-5B.
Setup cells:
  !git clone https://github.com/Wan-Video/Wan2.2 && pip install -r Wan2.2/requirements.txt
  !huggingface-cli download Wan-AI/Wan2.2-TI2V-5B --local-dir Wan2.2-TI2V-5B
Upload storyboard.json + outputs/keyframes/ as a Kaggle dataset, then: !python wan_shots.py
Download outputs/clips/*.mp4 back into the repo; shots.py picks them up automatically.
Each clip's latency is appended to runs_kaggle.jsonl; merge it into runs.jsonl."""
import json, subprocess, time, hashlib
from pathlib import Path

SB = json.loads(Path("storyboard.json").read_text())
OUT = Path("outputs/clips"); OUT.mkdir(parents=True, exist_ok=True)
SIZE = "832*480"  # draft resolution to save quota; switch to 1280*704 for chosen shots

for s in SB["shots"]:
    out = OUT / f"{s['id']}.mp4"
    key = hashlib.sha256((s["motion_prompt"] + str(s["seed"]) + SIZE).encode()).hexdigest()[:12]
    marker = OUT / f"{s['id']}.{key}.done"
    if marker.exists():
        print("cached", s["id"]); continue
    t0 = time.time()
    cmd = ["python", "Wan2.2/generate.py", "--task", "ti2v-5B", "--size", SIZE,
           "--ckpt_dir", "Wan2.2-TI2V-5B", "--offload_model", "True", "--convert_model_dtype", "--t5_cpu",
           "--image", f"outputs/keyframes/{s['id']}.jpg", "--prompt", s["motion_prompt"],
           "--base_seed", str(s["seed"]), "--save_file", str(out)]
    status = "ok"
    try:
        subprocess.run(cmd, check=True)
        marker.touch()
    except subprocess.CalledProcessError as e:
        status = f"error: {e}"  # e.g. CUDA OOM -> shot falls back to Ken Burns
    dt = time.time() - t0
    with open("runs_kaggle.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": "shots", "model": "wan2.2-ti2v-5b",
                            "params": {"shot": s["id"], "size": SIZE, "prompt": s["motion_prompt"]}, "seed": s["seed"],
                            "latency_s": round(dt, 1), "gpu_minutes": round(dt / 60, 2), "cost_usd": 0, "status": status}) + "\n")
    print(s["id"], status, f"{dt:.0f}s")
