import functools
import logging
import os

from dotenv import load_dotenv
from omegaconf import OmegaConf

logger = logging.getLogger(__name__)


env_path = os.path.abspath(".env")
load_dotenv(dotenv_path=env_path)


@functools.lru_cache
def _load_config(config_dir: str = "./config"):
    # Read default config
    try:
        current_config = OmegaConf.load(f"{config_dir}/default.yml")
    except FileNotFoundError:
        current_config = OmegaConf.create()

    # Read environment-dependent config
    delphai_environment = os.environ.get("DELPHAI_ENVIRONMENT")
    if not delphai_environment:
        raise Exception("DELPHAI_ENVIRONMENT is not defined")

    try:
        environment_config = OmegaConf.load(f"{config_dir}/{delphai_environment}.yml")
        current_config = OmegaConf.merge(current_config, environment_config)
    except FileNotFoundError:
        pass

    OmegaConf.set_readonly(current_config, True)
    return current_config


@functools.lru_cache
def get_config(path: str = "", config_dir: str = "./config"):
    config = _load_config(config_dir=config_dir)
    if path is None:
        return config
    selected = OmegaConf.select(config, path)
    if OmegaConf.is_config(selected):
        return OmegaConf.to_container(selected, resolve=True)
    else:
        return selected
