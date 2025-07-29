import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, available_timezones


def ask_yes_no(question: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{question} {suffix}: ").strip().lower()
        if answer == "" and default is not None:
            return default
        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'.")


def ask_string(question: str, default: str = "") -> str:
    suffix = f"[{default}]" if default else ""
    answer = input(f"{question} {suffix}: ").strip()
    return answer if answer else default


def generate_event_type_from_path(path: str) -> str:
    filename = Path(path).name
    return filename.replace(".", "_")


def run_setup_wizard(config_path: Path = Path("realtimeresults_config.json")):
    try:
        print("Welcome to the RealtimeResults setup wizard.")
        print("This wizard will help you generate a realtimeresults config file.")
        print("Json and toml formats are supported. Default config is realtimeresults_config.json.")

        config = {}

        # --- BACKEND STRATEGY ---
        config["backend_strategy"] = "sqlite"  # fixed default
        config["sqlite_path"] = "eventlog.db"

        # --- ENABLE VIEWER ---
        use_viewer = ask_yes_no("Do you want to enable the viewer backend? (Required to use Dashboard)", True)
        if use_viewer:
            viewer_host = ask_string("Viewer backend host", "127.0.0.1")
            viewer_port = int(ask_string("Viewer backend port", "8000"))
        else:
            viewer_host = "NONE"
            viewer_port = 0
        config["viewer_backend_host"] = viewer_host
        config["viewer_backend_port"] = viewer_port

        # --- ENABLE INGEST API ---
        use_ingest = ask_yes_no(
            "Do you want to enable the ingest backend? (Required for logging via API)", True
        )
        if use_ingest:
            ingest_host = ask_string("Ingest backend host", "127.0.0.1")
            ingest_port = int(ask_string("Ingest backend port", "8001"))
            config["ingest_backend_host"] = ingest_host
            config["ingest_backend_port"] = ingest_port

            # --- APPLICATION LOGGING ---
            support_app_logs = ask_yes_no("Do you want to support application log tailing?", True)
            source_log_tails = []
            while support_app_logs:
                log_path = ask_string("Enter the log file path relative to the config file")
                log_label = ask_string("Enter a label for this source")
                event_type = generate_event_type_from_path(log_path)
                timezone = ask_string("Enter timezone (e.g. Europe/Amsterdam)", ZoneInfo("localtime").key if "localtime" in available_timezones() else "UTC")

                source_log_tails.append({
                    "path": log_path,
                    "label": log_label,
                    "poll_interval": 1.0,
                    "event_type": event_type,
                    "log_level": "INFO",
                    "tz_info": timezone
                })
                support_app_logs = ask_yes_no("Do you want to add another log file?", False)

            config["source_log_tails"] = source_log_tails
        else:
            config["ingest_backend_host"] = "NONE"
            config["ingest_backend_port"] = 0
            config["source_log_tails"] = []

        # --- STRATEGY / SINK TYPES ---
        config["listener_sink_type"] = ask_string("Sink type for Robot Framework listener", "sqlite")
        if use_ingest:
            config["ingest_sink_type"] = ask_string("Sink type for the ingest API", "asyncsqlite")
        else:
            config["ingest_sink_type"] = "NONE"

        # --- LOG LEVELS ---
        config["log_level"] = "INFO"
        config["log_level_listener"] = ""
        config["log_level_backend"] = ""
        config["log_level_cli"] = ""

        # --- LOKI PLACEHOLDER ---
        config["loki_endpoint"] = "http://localhost:3100"

        # --- BACKEND ENDPOINT ---
        config["backend_endpoint"] = f"http://{viewer_host}:{viewer_port}" if use_viewer else "NONE"

        # --- WRITE TO FILE ---
        config_path = Path(config_path)
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"\nConfiguration complete. Config written to: {config_path.resolve()}")

        return ask_yes_no("Start tests?", True)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user (Ctrl+C). No config file was written.")
        sys.exit(130)