import dotenv
import os
def get_envconf():
    dotenv_file = dotenv.find_dotenv(os.environ['conf_file_path'])
    return dotenv_file


