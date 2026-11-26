"""Stage: keyframes. Character reference first, then one keyframe per shot via Cloudflare Workers AI.
Consistency comes from the fixed character description + style block attached to every prompt."""
import base64, os, sys, time
from common import OUT, Cache, input_hash, load_env, load_storyboard, log_call, retry, http_json, ffmpeg

API = "https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"


def gen_image(model, prompt, seed):
    url = API.format(acct=os.environ["CLOUDFLARE_ACCOUNT_ID"], model=model)
    r = http_json(url, {"prompt": prompt[:2048], "steps": 4, "seed": seed},
                  {"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"})
    return base64.b64decode(r["result"]["image"])


def build_prompt(sb, s):
    p = s["image_prompt"]
    if s.get("use_character"):
        c = sb["character"]
        p = f"{p}. The man is {c['name']}: {c['description']}"
    return f"{p}. {sb['style_block']}"


def placeholder(out, text):
    ffmpeg("-f", "lavfi", "-i", "color=c=0x3a2f25:s=1024x1024", "-frames:v", "1",
           "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=48:x=(w-tw)/2:y=(h-th)/2", out)


def main(force_placeholder=False):
    load_env()
    sb = load_storyboard()
    model = sb["models"]["image"]
    d = OUT / "keyframes"; d.mkdir(parents=True, exist_ok=True)
    cache = Cache("keyframes")
    live = not force_placeholder and os.environ.get("CLOUDFLARE_API_TOKEN")
    c = sb["character"]
    jobs = [("reference", f"{c['reference_prompt']}, {c['description']}. {sb['style_block']}", c["seed"])]
    jobs += [(s["id"], build_prompt(sb, s), s["seed"]) for s in sb["shots"]]
    for key, prompt, seed in jobs:
        out = d / f"{key}.jpg"
        h = input_hash(model, prompt, seed, bool(live))
        if cache.fresh(key, h, out):
            print(f"[keyframes] {key} cached"); continue
        t0 = time.time()
        if live:
            out.write_bytes(retry(lambda: gen_image(model, prompt, seed)))
            log_call("keyframes", model, {"shot": key, "seed": seed, "steps": 4, "prompt": prompt}, time.time() - t0)
        else:
            placeholder(out, key)
            log_call("keyframes", "placeholder", {"shot": key, "seed": seed}, time.time() - t0, note="no Cloudflare token")
        cache.put(key, h)
        print(f"[keyframes] {key} generated")


if __name__ == "__main__":
    main("--placeholder" in sys.argv)
