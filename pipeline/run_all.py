"""One command: validate -> narration -> keyframes -> music -> shots -> assemble.
Each stage reads storyboard.json and skips anything whose inputs have not changed.
Usage: python pipeline/run_all.py [--placeholder]   (--placeholder = dry run without API keys)"""
import sys, time
import narration, keyframes, music, shots, assemble
from common import load_storyboard

if __name__ == "__main__":
    ph = "--placeholder" in sys.argv
    t0 = time.time()
    load_storyboard(); print("[validate] storyboard.json OK")
    narration.main(placeholder=ph)
    keyframes.main(force_placeholder=ph)
    music.main()
    shots.main()
    assemble.main()
    print(f"done in {time.time() - t0:.1f}s")
