"""
CLI tool for automatically generating the docker files and running the env portal
"""
import click
import subprocess
from importlib.resources import files
from portal_env.config import config
from portal_env.utils import docker_image_exists, ensure_docker_network_exists
from pathlib import Path

supported_envs_aliases = {
    "atari": "ale",
}
supported_envs = [
    "ale",
    "mujoco",
    "retro",
]


def run_env(env_name: str, detach: bool, build_flag: bool, custom_path: Path):
    # Locate the path to the target env directory
    env_path = files("portal_env.envs").joinpath(env_name)
    pkg_path = files("portal_env")

    if custom_path is not None:
        dockerfile_path = custom_path / "Dockerfile.env"
        env_main_path = custom_path / "env_main.py"
        assert dockerfile_path.exists() and env_main_path.exists(), "Custom path must contain Dockerfile.env and env_main.py files"
    else:
        dockerfile_path = f"Dockerfile.env"

    # Convert to string path
    env_dir = str(env_path) if custom_path is None else str(custom_path)

    # Run docker build and run using that directory as the working dir
    # subprocess.run(["docker", "build", "-f", "Dockerfile.env", "-t", config.host_name, "."], cwd=env_dir, check=True)
    container_name = f"{config.host_name}_{env_name}"
    image_name = container_name
    if build_flag or (not docker_image_exists(image_name)):
        print("Building image...")
        subprocess.run(["docker", "build", "-f", dockerfile_path, "-t", image_name, "."], cwd=env_dir, check=True)

    # Check if a docker network exists, create if not:
    ensure_docker_network_exists(config.docker_network_name)

    # Run the container:
    run_args = [
        "docker", "run", "--rm", "--name", container_name, "-v", ".:/app/portal_env",
        "-p", f"{config.port}:{config.port}", "--network", config.docker_network_name,
    ]
    if detach:
        run_args.append("-d")
    run_args.append(image_name)
    subprocess.run(run_args, cwd=str(pkg_path), check=True)


@click.command()
@click.argument("env_name")
@click.option("-d", "--detach", is_flag=True, help="Run the Docker container in detached mode")
@click.option("-b", "--build", is_flag=True, help="Run the Docker container in detached mode")
@click.option("-p", "--path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
              help="Path to a directory containing custom Dockerfile.env and env_main.py files.")
def start(env_name: str, detach: bool, build: bool, path: Path = None):
    if env_name in supported_envs_aliases:
        env_name = supported_envs_aliases[env_name]
    if env_name not in supported_envs and path is None:
        raise ValueError(f"Unsupported env name: {env_name}")
    run_env(env_name, detach, build_flag=build, custom_path=path)


@click.command()
@click.argument("env_name")
def stop(env_name: str):
    pass


@click.group()
def main():
    pass


main.add_command(start)


if __name__ == '__main__':
    main()