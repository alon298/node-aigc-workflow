#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node AIGC Workflow - 节点化 AIGC 编排（参考 ComfyUI 节点范式）。"""
import argparse, json, time
from pathlib import Path

class Workflow:
    def __init__(self, name):
        self.name, self.nodes, self.state = name, [], {}

    def add(self, kind, **params):
        self.nodes.append({"kind": kind, "params": params})
        return self

    def run(self, out_dir="outputs"):
        out = Path(out_dir) / self.name
        out.mkdir(parents=True, exist_ok=True)
        for node in self.nodes:
            fn = NODES[node["kind"]]
            self.state.update(fn(self.state, node["params"], out) or {})
        (out / "manifest.json").write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
        return out / "manifest.json"

# ---------------- 节点实现 ----------------
def n_prompt(state, p, out):
    tpl = "电商产品短视频，{subject}，{style}，商业摄影质感，高清细节"
    return {"prompt": tpl.format(**p), "subject": p.get("subject", "")}

def n_first_frame(state, p, out):
    seed = p.get("seed", 20260801)
    frame = {"file": f"first_frame_{seed}.png", "seed": seed, "prompt": state["prompt"], "backend": p.get("backend", "mock")}
    (out / frame["file"]).write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)  # 占位
    return {"first_frame": frame}

def n_consistency_lock(state, p, out):
    return {"lock": {"character_seed": state["first_frame"]["seed"], "reference": state["first_frame"]["file"], "version": p.get("version", "v1")}}

def n_image_to_video(state, p, out):
    shots = []
    for i in range(p.get("count", 5)):
        shots.append({"shot": i + 1, "motion": p.get("motions", ["缓推", "环绕", "特写拉远", "平移", "定格"])[i % 5],
                      "source": state["first_frame"]["file"], "seed": state["lock"]["character_seed"] + i,
                      "duration": p.get("duration", 3)})
    return {"shots": shots}

def n_batch_output(state, p, out):
    return {"batch": {"count": len(state["shots"]), "manifest": str(out / "manifest.json"), "ts": time.time()}}

NODES = {"prompt": n_prompt, "first_frame": n_first_frame, "consistency_lock": n_consistency_lock,
         "image_to_video": n_image_to_video, "batch_output": n_batch_output}

def build(shots=5):
    return (Workflow("ecom_video")
            .add("prompt", subject="冰感男士内裤", style="夏日清爽场景")
            .add("first_frame", seed=20260801)
            .add("consistency_lock", version="v1")
            .add("image_to_video", count=shots)
            .add("batch_output"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, default=5)
    args = ap.parse_args()
    manifest = build(args.shots).run()
    print(f"工作流执行完成 -> {manifest}")
    st = json.loads(Path(manifest).read_text(encoding="utf-8"))
    for s in st["shots"]:
        print(f"  镜头{s['shot']}: {s['motion']} {s['duration']}s seed={s['seed']}（一致性种子继承）")
