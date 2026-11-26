"""Stage: narration. One WAV per shot from Gemini TTS. Cached by (model, voice, style, line)."""
import base64, os, sys, time, wave
from common import OUT, Cache, input_hash, load_env, load_storyboard, log_call, retry, http_json, ffmpeg

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def tts(model, voice, text):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    r = http_json(API.format(model=model), body, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    return base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])  # 24 kHz s16le mono PCM


def main(placeholder=False):
    load_env()
    sb = load_storyboard()
    m = sb["models"]
    d = OUT / "narration"; d.mkdir(parents=True, exist_ok=True)
    cache = Cache("narration")
    for s in sb["shots"]:
        out = d / f"{s['id']}.wav"
        h = input_hash(m["tts"], m["tts_voice"], m["tts_style"], s["narration"], placeholder)
        if cache.fresh(s["id"], h, out):
            print(f"[narration] {s['id']} cached"); continue
        t0 = time.time()
        if placeholder or not os.environ.get("GEMINI_API_KEY"):
            # Silent placeholder so assembly still runs without a key (radio-cut dry run).
            ffmpeg("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", s["duration"] - 1, out)
            log_call("narration", "placeholder-silence", {"shot": s["id"]}, time.time() - t0, note="no GEMINI_API_KEY")
        else:
            pcm = retry(lambda: tts(m["tts"], m["tts_voice"], f"{m['tts_style']} {s['narration']}"))
            with wave.open(str(out), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
            log_call("narration", m["tts"], {"shot": s["id"], "voice": m["tts_voice"], "chars": len(s["narration"])},
                     time.time() - t0)
        cache.put(s["id"], h)
        print(f"[narration] {s['id']} generated")


if __name__ == "__main__":
    main(placeholder="--placeholder" in sys.argv)
