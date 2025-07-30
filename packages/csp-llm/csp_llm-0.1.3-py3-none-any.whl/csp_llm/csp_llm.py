#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_required_tools import check_app_dependencies, find_app_path, require_java


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Launch the application")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8501)
    parser.add_argument("-ev", action="store_true")

    args = parser.parse_args()

    APP_FILE = find_app_path("main.py")

    HOST = args.host  # or "0.0.0.0" for whole network access
    PORT = args.port  # default

    print("🚀 Launching the application...")

    # Vérifier que le fichier existe
    app_path = Path(APP_FILE)
    if not app_path.exists():
        print(f"❌ Error: {APP_FILE} not found")

        return 1

    print("💡 Application dependencies")

    install_messages, are_packages_ok = check_app_dependencies()

    print("\n".join(install_messages))

    if not all(are_packages_ok):
        return 1

    if not require_java(8):
        print("❌ Java 8+ required to use pycsp3")
        return 1

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        APP_FILE,
        "--server.address",
        HOST,
        "--server.port",
        str(PORT),
        "--logger.level",
        "error",
        "--browser.gatherUsageStats",
        "false",
        "server.maxUploadSize",
        "5",
    ]

    # Afficher l'URL d'accès
    print(f"🌐 Application available at: http://{HOST}:{PORT}")
    print("💡 Press Ctrl+C to stop")
    print("-" * 50)

    try:

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Application stopped")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
