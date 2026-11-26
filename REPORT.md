# Report: The Heritage Short

> Draft. Replace every TODO with what really happened, in your own words. Export to PDF/Word to submit.

**What I set out to make, and for whom.** A 60–90 s film about TODO (the person/story), narrated in Amharic with English subtitles, for TODO (audience), so that they TODO (intent).

**What I learned from my audience.** Radio-cut test: TODO (who, what they said, what I changed in storyboard.json). Near-final test: TODO.

**Hardest problem and how I solved it.** Time and GPU quota. A Wan 2.2 clip takes minutes on a Kaggle T4, and I started late. I designed the shots stage so that every shot has a deterministic Ken Burns fallback over its keyframe, and real Wan clips replace it automatically when they appear in `outputs/clips/`. The film is always complete, and quality improves as GPU time allows. TODO: add any other real blocker (Amharic TTS pronunciation, identity drift, quota).

**A suggested practice that beat my instinct.** The JSON contract plus input-hash caching. My instinct was to write one script. Keeping prompts, seeds and narration in `storyboard.json` meant that changing one line re-ran exactly one model call (evidence: runs.jsonl). TODO confirm / adjust.

**A suggested practice that did not work for me.** TODO (be honest, with evidence).

**Ceiling work.** TODO (if none, say so honestly and say what you would try first).

**What I would build next.** A small web form where a relative tells a story in Amharic and gets a storyboard.json back, so the pipeline becomes a tool for the family. Also a LoRA trained on the character sheet, measured against the current prompt-only consistency.
