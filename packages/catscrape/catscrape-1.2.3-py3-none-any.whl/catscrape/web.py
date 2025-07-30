from .data import *

# FUNCTIONS

def new_driver(headless: bool=True):
    """ Creates a new selenium driver """
    # Initalize the Chrome options object
    chrome_options = Options()

    # Disable verbosity
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-logging")

    # Change the user agent to avoid auto-blocking
    chrome_options.add_argument("user-agent=Chrome")

    # Add the headless tag if requested
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def get_website_html(url, use_java: bool=False):
    """ Return the HTML of the URL"""
    if use_java:
        # Java requires selenium

        # Create a new driver
        driver = new_driver()

        # Get the URL
        driver.get(url)

        # Wait for AJAX to load all of the elements.
        time.sleep(5)

        # driver.page_source will not work with some dynamic Java webpages, so use a custom script to return all HTML.
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        return html
    else:
        # Get the HTML with requests
        response = requests.get(url)
        
        return response.text