import time
import os

import html as html_lib
import requests
import warnings
import appdirs
import pickle
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# VARIABLES

FOLLOWERS = "FOLLOWERS"
FOLLOWING = "FOLLOWING"

ABOUT_ME = "ABOUT ME"
WORKING_ON = "WORKING ON"

LOGIN_URL = "https://scratch.mit.edu/login"

APP_NAME = "catscrape"

# APPDATA SETUP

# Get the AppData folder path
appdata_folder_path = appdirs.user_data_dir(APP_NAME)

# Create the appdata folder
os.makedirs(appdata_folder_path, exist_ok=True)

LOGIN_DATA_PATH = os.path.join(str(appdata_folder_path), "login.pkl")

# FUNCTIONS

def save_login_data(username:str, password:str):
    """ Saves the username and password in a file. Necessary for some functions that require authority, for instance, in a studio. """
    with open(LOGIN_DATA_PATH, "wb") as f:
        pickle.dump((username, password), f)
    print("Successfully saved the login data.")

def get_login_data():
    try:
        with open(LOGIN_DATA_PATH, "rb") as f:
            data = pickle.load(f)
    except FileNotFoundError:
        raise RuntimeError("There is no login data. Use `catscrape.save_login_data` to save login data to use this feature.")

    return data