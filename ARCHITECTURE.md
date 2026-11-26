# Architecture

## Contract
`storyboard.json` is the only interface between stages. It is validated against `schema/storyboard.schema.json` at the start of every stage (8–12 shots, required fields per shot, total duration 60–90 s). Prompts, seeds, voice, style block and music cues all live in the storyboard rather than in code, so a run can be reproduced and explained.

## Stages
```
storyboard.json ─► narration  ─► outputs/narration/sNN.wav
                ├► keyframes  ─► outputs/keyframes/reference.jpg, sNN.jpg
                ├► [Kaggle] Wan 2.2 ─► outputs/clips/sNN.mp4 (optional)
                ├► shots      ─► outputs/shots/{16x9,9x16}/sNN.mp4  (Wan clip, or Ken Burns fallback)
                ├► [Kaggle] ACE-Step ─► outputs/music/score.wav
                └► assemble   ─► outputs/final/heritage_short_{16x9,9x16}.mp4
```

## Caching
Each stage keeps `outputs/.cache/<stage>.json`, mapping item id → SHA-256 of the inputs that produced it (for example model + voice + style + line for narration, or model + full prompt + seed for keyframes). An item is regenerated only if its hash changed or its file is missing. Editing one narration line therefore causes exactly one TTS call. Assembly is deterministic FFmpeg and always re-runs, which takes seconds.

## Failure handling
- **Retries:** every API call goes through `common.retry` (3 attempts, exponential backoff 4 s / 8 s) to cover 429 quota responses and 5xx errors.
- **Graceful degradation:** with no API key a stage writes a placeholder (silence, a labelled card, a sine pad) and logs it, so the rest of the pipeline still runs. A missing or failed Wan clip falls back to a Ken Burns move over the keyframe.
- **Validation first:** invalid storyboards fail before any quota is spent.
- **Kaggle sessions time out:** `wan_shots.py` writes a `.done` marker per shot, so a restarted session resumes where it stopped.

## Logging
Every model or FFmpeg call appends one line to `runs.jsonl`: timestamp, stage, model, params, seed, latency, GPU minutes, cost, status.

## Audio
Narration lines are placed at each shot start (+0.4 s). The score is ducked using `sidechaincompress` (threshold 0.02, ratio 6, attack 300 ms, release 1500 ms), mixed, and normalised with `loudnorm` to −14 LUFS / −1 dBTP. Subtitles are generated from `subtitle_en` as SRT and burned in, with a larger bottom margin in 9:16 to stay inside the safe area.
