# 从环境变量中获取
import os


def get_env(env_name):
    getenv = os.getenv(env_name)
    if getenv is not None:
        return getenv
    else:
        print(f"获取{env_name}失败，请检查环境变量")