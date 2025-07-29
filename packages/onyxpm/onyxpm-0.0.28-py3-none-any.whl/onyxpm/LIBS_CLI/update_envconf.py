import dotenv
import os
from CLASSES.EnvConfElement import EnvConfElement


def update_envconf(ele:EnvConfElement):
    os.environ[ele.key] = ele.value
    dotenv.set_key(ele.filename, ele.key, os.environ[ele.key])

