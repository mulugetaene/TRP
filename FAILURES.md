# Failures

Format: what broke → what I tried → what fixed it / workaround.

> TODO (you): add real entries as they happen (quota, OOM, identity drift, Amharic pronunciation, Kaggle timeouts).

1. **Deadline and GPU time.** Kaggle Wan 2.2 runs take several minutes per clip on a T4, which did not fit the time left. → Built a Ken Burns fallback into `shots.py`, so every shot still has a moving picture; Wan clips replace them automatically when available.
2. **Running without API keys.** → Placeholder mode (`make dry-run`) so the pipeline can be checked end to end before any quota is spent.
