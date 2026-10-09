from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from pathlib import Path

from cuw.core.config import AgentConfig, BrokerConfig
from cuw.core.logging import setup_logging
from cuw.daemon.state_machine import StateMachine


def _interactive_setup() -> None:
    """Wizard that generates config.yaml based on user input."""
    print("⚙️  computeruse-watcher — Configuración interactiva")
    print("   (Enter para usar valores por defecto)")
    print()

    broker_host = input(f"Broker host [localhost]: ").strip() or "localhost"
    broker_port_str = input(f"Broker port [1883]: ").strip() or "1883"
    broker_user = input("Username (Enter para omitir): ").strip()
    broker_pass = input("Password (Enter para omitir): ").strip()

    try:
        broker_port = int(broker_port_str)
    except ValueError:
        print("⚠️  Puerto inválido, usando 1883")
        broker_port = 1883

    config_path = Path("config.yaml")
    config_content = f"""# computeruse-watcher configuration
broker:
  host: {broker_host}
  port: {broker_port}
  username: "{broker_user}"
  password: "{broker_pass}"
  tls: false
"""
    config_path.write_text(config_content, encoding="utf-8")
    print(f"\n✅ Configuración guardada en {config_path.resolve()}")
    print(f"\nPara ejecutar: python -m cuw.cli --config {config_path}")


def load_config(path: Path | None) -> AgentConfig:
    if path and path.exists():
        try:
            import yaml
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data:
                cfg = AgentConfig(**data)
                return cfg
        except Exception:
            pass
    return AgentConfig()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cuw",
        description="computeruse-watcher — Lightweight OS-agnostic computer usage telemetry agent",
    )
    parser.add_argument("--config", type=str, help="path to YAML config")
    parser.add_argument("--dry-run", action="store_true", help="run a single tick and exit")
    parser.add_argument("--setup", action="store_true", help="interactive setup wizard (generates config.yaml)")
    args = parser.parse_args()

    if args.setup:
        _interactive_setup()
        return

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