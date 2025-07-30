import time
import os
import re

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

VALID_USERNAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"

# FUNCTIONS

def find(s, seq):
    """ Finds the sequence in the string, raising an exception if not present. """
    loc = s.find(seq)
    #assert loc != -1
    return loc