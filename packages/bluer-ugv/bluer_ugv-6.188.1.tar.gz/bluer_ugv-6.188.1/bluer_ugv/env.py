import os
from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


BLUER_BEAST_MODEL = get_env("BLUER_BEAST_MODEL")
