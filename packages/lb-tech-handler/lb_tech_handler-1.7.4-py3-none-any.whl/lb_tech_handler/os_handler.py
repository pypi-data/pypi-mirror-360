import json
import os

def get_cpu_count() -> int:
    """Function to get cpu count

    Returns:
        int: Number of cpus
    """

    return os.cpu_count()

def get_all_env_variables() -> dict:
    """Function to get all env variables

    Returns:
        dict: _description_
    """

    env_data = {}

    for key, value in os.environ.items():
        env_data[key] = value

    return env_data

def get_env_variable(key:str) -> str:
    """Function to get env variable

    Args:
        key (str): _description_

    Returns:
        str: _description_
    """

    return os.getenv(key=key,default=None)


def set_env_variable(key:str,value:str):
    """Function to set env variable

    Args:
        key (str): _description_
        value (str): _description_
    """

    os.environ[key] = value


if __name__ == "__main__":
    print("env_data")

    # print(json.dumps(env_data,indent=4))