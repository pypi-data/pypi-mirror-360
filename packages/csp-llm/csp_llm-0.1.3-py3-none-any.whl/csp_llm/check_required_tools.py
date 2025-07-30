#!/usr/bin/env python3

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def check_pycsp3_pip() -> Optional[str]:

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "pycsp3"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            # Parser pip show output
            output = result.stdout

            version = "Unknown"
            location = "Unknown"

            for line in output.split("\n"):
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                elif line.startswith("Location:"):
                    location = line.split(":", 1)[1].strip()

            # return {"version":version, "location":location}
            return version

        return None

    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        return None


# find main app file path automatically in src/
def find_app_path(app_file_name: str) -> Path:

    possible_locations = [
        # in same package with script ?
        Path(__file__).parent / app_file_name,
        # in /src from project root ?
        Path(__file__).parent.parent.parent / "src" / app_file_name,
        # in current directory ?
        Path.cwd() / "src" / app_file_name,
        Path.cwd() / app_file_name,
    ]

    for location in possible_locations:
        if location.exists():
            return location.resolve()  # absolute path

    raise FileNotFoundError("app file not found")


def check_app_dependencies() -> tuple[list[str], list[bool]]:

    count = 0
    total = 6

    are_packages_ok: list[bool] = [True] * total
    install_messages: list[str] = []
    try:
        import anthropic

        install_messages.append(f"✅ anthropic {anthropic.__version__}")
    except ImportError:
        install_messages.append("❌ anthropic is not installed")
        are_packages_ok[count] = False
        count += 1

    try:
        import openai

        install_messages.append(f"✅ openai {openai.__version__}")
    except ImportError:
        install_messages.append("❌ openai is not installed")
        are_packages_ok[count] = False
        count += 1

    try:
        import streamlit

        install_messages.append(f"✅ streamlit {streamlit.__version__}")
    except ImportError:
        install_messages.append("❌ streamlit is not installed")
        are_packages_ok[count] = False
        count += 1
    try:
        import streamlit_ace

        install_messages.append(f"✅ streamlit_ace {streamlit_ace.__version__}")
    except ImportError:
        install_messages.append("❌ streamlit_ace is not installed")
        are_packages_ok[count] = False
        count += 1
    try:
        import dotenv

        install_messages.append(f"✅ {dotenv.__name__}")
    except ImportError:
        install_messages.append("❌ dotenv is not installed")
        are_packages_ok[count] = False
        count += 1

    pycsp_version = check_pycsp3_pip()
    if pycsp_version:
        install_messages.append(f"✅ pycsp3 {pycsp_version}")
    else:
        install_messages.append("❌ pycsp3 is not installed")
        are_packages_ok[count] = False
        count += 1

    return install_messages, are_packages_ok


def check_java_installed() -> Optional[dict]:

    java_commands = ["java", "java.exe"]

    for java_cmd in java_commands:
        java_path = shutil.which(java_cmd)
        if not java_path:
            continue

        try:
            result = subprocess.run(
                [java_cmd, "-version"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            version_output = result.stderr

            if result.returncode == 0 and version_output:
                return parse_java_version(version_output, java_path)

        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            continue

    return None


def parse_java_version(version_output: str, java_path: str) -> Optional[dict]:

    try:
        lines = version_output.strip().split("\n")

        version_line = lines[0] if lines else ""
        version_match = re.search(r'version\s+"([^"]+)"', version_line)
        if not version_match:
            return None

        version_string = version_match.group(1)
        major_version = extract_major_version(version_string)

        vendor = "Unknown"
        runtime = "Unknown"
        is_openjdk = False

        if "openjdk" in version_line.lower():
            vendor = "OpenJDK"
            is_openjdk = True
        elif "oracle" in version_line.lower():
            vendor = "Oracle"
        elif "ibm" in version_line.lower():
            vendor = "IBM"
        elif "amazon" in version_line.lower():
            vendor = "Amazon Corretto"
        elif "zulu" in version_line.lower():
            vendor = "Azul Zulu"

        if len(lines) > 1:
            runtime_line = lines[1]
            if "Runtime Environment" in runtime_line:
                runtime = runtime_line.strip()
            elif "OpenJDK Runtime Environment" in runtime_line:
                runtime = "OpenJDK Runtime Environment"
                is_openjdk = True

        return {
            "version": version_string,
            "major_version": major_version,
            "vendor": vendor,
            "runtime": runtime,
            "path": java_path,
            "is_openjdk": is_openjdk,
        }

    except Exception as e:
        print(f"Error parsing Java version: {e}")
        return None


def extract_major_version(version_string: str) -> int:

    try:
        clean_version = re.sub(r"[+-].*$", "", version_string)

        parts = clean_version.split(".")

        if len(parts) >= 2 and parts[0] == "1":
            return int(parts[1])
        elif len(parts) >= 1:
            return int(parts[0])
        else:
            return 0

    except (ValueError, IndexError):
        return 0


def require_java(min_version: int = 8) -> bool:

    java_info: dict | None = check_java_installed()

    if not java_info:
        print(f"❌ Java {min_version}+ required but not installed")
        print("💡 Install Java from: https://adoptium.net/")
        return False

    if int(java_info.get("major_version")) < min_version:
        print(f"❌ Java {min_version}+ required")
        print(
            f"   installed version: {java_info.get('version')} (major: {java_info.get('major_version')})"
        )
        print("💡 Update Java to a newer version")
        return False

    print(f"✅ Java {java_info.get('version')} detected (>= {min_version})")
    return True
