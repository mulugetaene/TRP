# Experiments

Format: hypothesis → change (one thing, fixed seed) → result (evidence: runs.jsonl line / observation) → decision.

> TODO (you): record only experiments you actually ran. Candidates that fit this pipeline:

1. **Character consistency:** attaching the full character description to every prompt vs. the name only → compare drift across s02/s05/s06.
2. **Seed control:** same prompt, seeds 105 vs 205 → how much the composition changes.
3. **TTS style instruction:** no style vs. "calm, warm, unhurried" → listener preference and duration per line.
4. **TTS voice:** Kore vs. another voice for Amharic pronunciation of names.
5. **Narration speed:** measured words/second in Amharic vs. the 2–2.5 English guideline → effect on shot durations.
6. **Wan resolution:** 832×480 vs 1280×704 → latency and GPU minutes per clip.
7. **Wan motion prompt:** motion-only vs. re-describing the subject → artifacts.
8. **Ken Burns vs Wan:** for the same shot, which do viewers prefer?
9. **ACE-Step candidates:** 3 seeds → which one sits best under the voice, and why.
10. **Ducking settings:** ratio 6 vs 10 → narration intelligibility on a phone speaker.
