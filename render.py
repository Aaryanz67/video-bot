"""Usage: python render.py --theme progress|newstart --line1 "small steps" --line2 "still count." --out out/video.mp4"""
import argparse, os, sys
import make_v2 as m
from make_videos import render

p = argparse.ArgumentParser()
p.add_argument("--theme", required=True, choices=["progress", "newstart"])
p.add_argument("--line1", required=True)
p.add_argument("--line2", required=True)
p.add_argument("--out", default="out/video.mp4")
a = p.parse_args()

l1, l2 = a.line1.strip().lower()[:30], a.line2.strip().lower()[:30]
if a.theme == "progress":
    m.LINE_A[:] = [l1, l2]; fn, dur = m.scene_a2, 9.5
else:
    m.LINE_C[:] = [l1, l2]; fn, dur = m.scene_c2, 8.0
os.makedirs("out", exist_ok=True)
name = "job"
render(name, fn, dur)
os.replace(f"out/{name}.mp4", a.out)
