# Score generation with ACE-Step 1.5 (Kaggle / Colab GPU)

1. `git clone https://github.com/ACE-Step/ACE-Step-1.5` and follow its README install steps.
2. Use the caption, bpm and key from `storyboard.json -> music` (tempo and key go in the metadata fields, not in the caption). Duration = total film length.
3. Generate 3 candidates (3 seeds), save as `outputs/music/candidate_{1,2,3}.wav`.
4. Listen to each under the narration at low volume. Copy the chosen one to `outputs/music/score.wav` and record why in EXPERIMENTS.md.
5. Log each generation (seed, latency, GPU minutes) as a line in runs.jsonl.
