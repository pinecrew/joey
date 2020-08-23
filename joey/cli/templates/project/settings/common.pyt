import yaml
import typing
from pathlib import Path

conf = Path(__file__).parent / 'common.yml'
vars().update(yaml.load(conf.open(), Loader=yaml.Loader))

PROJECT_NAME: str = '${app_name}'
