# Costs

All stages used free tiers: $0 spent. Figures come from `runs.jsonl` (sum latency_s / gpu_minutes per stage).

| Stage | Calls | Total latency | GPU minutes | Free limit found | List-price equivalent |
|---|---|---|---|---|---|
| narration (Gemini TTS) | TODO | TODO | – | TODO | TODO |
| keyframes (FLUX schnell, CF) | TODO | TODO | – | ~50–170 images/day | TODO |
| shots (Wan 2.2, Kaggle T4) | TODO | TODO | TODO | ~30 GPU h/week | TODO (T4 ≈ $0.35/h on cloud) |
| music (ACE-Step) | TODO | TODO | TODO | – | TODO |
| assembly (FFmpeg, local) | TODO | TODO | – | – | $0 |

Quick sum per stage:
```bash
python3 -c "import json,collections as c;d=c.defaultdict(lambda:[0,0,0]);[ (lambda r:(d[r['stage']].__setitem__(0,d[r['stage']][0]+1),d[r['stage']].__setitem__(1,d[r['stage']][1]+r['latency_s']),d[r['stage']].__setitem__(2,d[r['stage']][2]+r.get('gpu_minutes',0))))(json.loads(l)) for l in open('runs.jsonl')];[print(k,*v) for k,v in d.items()]"
```
Frontier comparison: no frontier access this cohort.
