import subprocess
import logging
from glob import glob
import yaml
import os
import shutil

log = logging.getLogger(__name__)


def docker_up():
    log.info("🐳 Starting Docker environment...")
    env = os.environ.copy()
    env["AIRFLOW_UID"] = "50000"
    env["AIRFLOW_GID"] = "0"
    env["DOCKER_INSECURE_NO_IPTABLES_RAW"] = "1"

    local_compose_file = "docker-compose.yml"
    if not os.path.exists(local_compose_file):
        log.info("📋 Creating docker-compose.yml ...")

        package_compose_file = os.path.join(
            os.path.dirname(__file__), "docker-compose.yml")
        shutil.copy2(package_compose_file, local_compose_file)
        log.info("✅ docker-compose.yml create successfully!")

    # Verifica se a pasta dags existe
    dags_path = "dags"
    if not os.path.exists(dags_path):
        log.info("📁 Create 'dags' directory...")
        os.makedirs(dags_path, exist_ok=True)

    try:
        subprocess.run(["docker", "compose", "up", "-d"], env=env, check=True)
        log.info("✅ Docker environment is ready: http://localhost:8080")
    except subprocess.CalledProcessError as e:
        log.error(f"❌ Error Docker: {e}")
        log.error("Check if Docker is running and try again.")
        raise


def docker_down():
    log.info("🐳 Stopping Docker environment...")
    subprocess.run(["docker", "compose", "down"], check=False)


def run_dag():
    log.info("🚀 Running DAG in Docker...")
    try:
        config = glob("dags/*/config.yml").pop()
        with open(config, "r") as file:
            config_data = yaml.safe_load(file)
            dag_id = config_data['args']["id"]

        subprocess.run([
            "docker", "exec", "-it", "airflow-worker-container",
            "airflow", "dags", "test", dag_id
        ], check=True)
        log.info(f"✅ DAG '{dag_id}' executed successfully.")
    except Exception as e:
        log.error(f"❌ Error running DAG: {e}")


def fix_python_code():
    log.info("🔧 Running flake8 on 'dags' folder...")
    try:
        subprocess.run(["flake8", "dags"], check=True)
        log.info("✅ Code checked with flake8.")
    except subprocess.CalledProcessError as e:
        log.error(f"❌ flake8 found issues: {e}")
