import configparser
import os

def read_config(filename="config.ini"):
    config = configparser.ConfigParser()

    if not os.path.exists(filename):
        print("[X] ไม่พบ config.ini")
        return config

    config.read(filename, encoding="utf-8")
    return config
