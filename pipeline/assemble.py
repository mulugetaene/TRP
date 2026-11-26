"""Stage: assembly (deterministic, FFmpeg only).
Concat shots + end card, place narration at each shot start, duck the score under the voice
(sidechaincompress), burn English subtitles, normalise to -14 LUFS / -1 dBTP, export 16:9 and 9:16."""
import time
from common import ROOT, OUT, load_storyboard, log_call, ffmpeg

SIZES = {"16x9": (1280, 720), "9x16": (720, 1280)}


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(sb, path):
    t, lines = 0.0, []
    for i, s in enumerate(sb["shots"], 1):
        lines += [str(i), f"{srt_time(t + 0.3)} --> {srt_time(t + s['duration'] - 0.3)}", s["subtitle_en"], ""]
        t += s["duration"]
    path.write_text("\n".join(lines), encoding="utf-8")


def end_card(sb, tag, w, h, out):
    fs = 40 if w > h else 34
    ffmpeg("-f", "lavfi", "-i", f"color=c=black:s={w}x{h}:r=24:d={sb['end_card']['duration']}",
           "-vf", f"drawtext=text='{sb['end_card']['text']}':fontcolor=white:fontsize={fs}:x=(w-tw)/2:y=(h-th)/2,"
                  "fade=t=in:d=0.5,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", out)


def main():
    sb = load_storyboard()
    final = OUT / "final"; final.mkdir(parents=True, exist_ok=True)
    srt = final / "subtitles_en.srt"; write_srt(sb, srt)
    total = sum(s["duration"] for s in sb["shots"]) + sb["end_card"]["duration"]

    # 1. Narration track: each shot's line delayed to the shot start (+0.4s breath).
    inputs, delays, t = [], [], 0.0
    for i, s in enumerate(sb["shots"]):
        inputs += ["-i", OUT / "narration" / f"{s['id']}.wav"]
        delays.append(f"[{i}:a]aresample=48000,adelay={int((t + 0.4) * 1000)}:all=1[n{i}]")
        t += s["duration"]
    n = len(sb["shots"])
    voice = final / "voice.wav"
    ffmpeg(*inputs, "-filter_complex", ";".join(delays) + ";" + "".join(f"[n{i}]" for i in range(n)) +
           f"amix=inputs={n}:normalize=0,apad,atrim=0:{total}[v]", "-map", "[v]", "-ac", "2", voice)

    # 2. Duck the score under the voice and mix.
    music = ROOT / sb["music"]["chosen_file"]
    mix = final / "mix.wav"
    ffmpeg("-i", voice, "-stream_loop", "-1", "-i", music, "-filter_complex",
           f"[1:a]atrim=0:{total},aresample=48000,volume=0.5[m];[0:a]asplit[v1][v2];"
           "[m][v1]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[duck];"
           f"[v2][duck]amix=inputs=2:normalize=0,afade=t=out:st={total-2}:d=2,"
           "loudnorm=I=-14:TP=-1:LRA=11[out]", "-map", "[out]", "-ar", "48000", mix)

    # 3. Picture per aspect ratio, subtitles burned in, mux.
    for tag, (w, h) in SIZES.items():
        t0 = time.time()
        card = final / f"endcard_{tag}.mp4"; end_card(sb, tag, w, h, card)
        lst = final / f"concat_{tag}.txt"
        files = [OUT / "shots" / tag / f"{s['id']}.mp4" for s in sb["shots"]] + [card]
        lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
        style = "FontSize=16,MarginV=40,Outline=1" if w > h else "FontSize=12,MarginV=140,Outline=1"  # vertical safe area
        out = final / f"heritage_short_{tag}.mp4"
        ffmpeg("-f", "concat", "-safe", 0, "-i", lst, "-i", mix,
               "-vf", f"subtitles={srt}:force_style='{style}'", "-map", "0:v", "-map", "1:a",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", 20, "-r", 24, "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", out)
        log_call("assemble", "ffmpeg", {"aspect": tag, "duration": total}, time.time() - t0)
        print(f"[assemble] wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
