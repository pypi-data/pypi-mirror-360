import logging
import subprocess

log = logging.getLogger(__name__)


def check_docker():
    try:
        subprocess.check_output(["docker", "--version"])
        subprocess.check_output(["docker", "info"])
        log.info("✅ Docker is installed and running.")
        return True
    except Exception as e:
        log.error(f"❌ Docker check failed: {e}")
        return False
