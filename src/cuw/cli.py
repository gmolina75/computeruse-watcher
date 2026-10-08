from __future__ import annotations
import argparse
import signal
import sys
import time
from pathlib import Path

from cuw.core.config import AgentConfig
from cuw.core.logging import setup_logging
from cuw.daemon.state_machine import StateMachine

def load_config(path: Path | None) -> AgentConfig:
    if path and path.exists():
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cfg = AgentConfig(**data)
    else:
        cfg = AgentConfig()
    return cfg

def main() -> None:
    p = argparse.ArgumentParser(description="computeruse-watcher daemon")
    p.add_argument("--config", type=str, help="path to YAML config")
    p.add_argument("--dry-run", action="store_true", help="run a single tick and exit")
    args = p.parse_args()

    cfg = load_config(Path(args.config) if args.config else None)
    setup_logging(level="INFO", log_path=cfg.log_path)

    sm = StateMachine(cfg)
    sm.start()

    stop = False
    def handler(_sig, _frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGINT, handler)
    try:
        if args.dry_run:
            sm.tick()
            print("Dry-run tick completed.")
        else:
            interval = max(0.5, cfg.poll_interval_sec)
            while not stop:
                sm.tick()
                time.sleep(interval)
    finally:
        sm.stop()

if __name__ == "__main__":
    main()
