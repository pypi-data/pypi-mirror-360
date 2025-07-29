import argparse
import logging
import sys
from .os_utils import check_docker
from .docker_utils import docker_up, docker_down, run_dag, fix_python_code

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Airflow Docker Helper CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("up", help="Start Docker environment")

    subparsers.add_parser("down", help="Stop Docker environment")

    subparsers.add_parser("run", help="Run Airflow DAG inside Docker")

    subparsers.add_parser("fix", help="Run flake8 linter")

    args = parser.parse_args()

    if not check_docker():
        log.error("❌ Docker not ready.")
        sys.exit(1)

    if args.command == "up":
        docker_up()
    elif args.command == "down":
        docker_down()
    elif args.command == "run":
        run_dag()
    elif args.command == "fix":
        fix_python_code()
    else:
        parser.print_help()
