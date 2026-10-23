"""Append outbox/summary.md to a local simulated channel log.

This does not send a real message. Each run appends to outbox/channel_log.md.
"""
import datetime
import os
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "outbox/summary.md"
os.makedirs("outbox", exist_ok=True)
with open(SRC) as f:
    body = f.read()
with open("outbox/channel_log.md", "a") as log:
    log.write(f"\n\n===== posted {datetime.datetime.now().isoformat()} to #customer-weekly =====\n")
    log.write(body)
print("posted to #customer-weekly (simulated)")
