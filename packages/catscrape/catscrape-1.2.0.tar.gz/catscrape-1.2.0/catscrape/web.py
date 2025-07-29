from .data import *

# FUNCTIONS

def new_driver(headless: bool=True):
    """ Creates a new selenium driver """
    # Initalize the Chrome options object to change settings for the driver
    chrome_options = Options()

    # Disable verbosity
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--v=0")

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

        # Wait for AJAX to load all of the elements. The thumbnail image is most likely the last to load, but wait a second after just to be sure.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "thumbnail-image"))
        )
        time.sleep(1)

        # driver.page_source will not work with some dynamic Java webpages, so use a custom script to return all HTML in the body.
        # This has the added benefit of not including the CSS for better performance.
        html = driver.execute_script("return document.getElementsByTagName('body')[0].innerHTML")#driver.page_source[:]
        return html
    else:
        # Get the HTML with requests
        response = requests.get(url)

        # Make sure the scrape was successful
        response.raise_for_status()
        
        return response.text

def login():
    """ Login to Scratch """
    # Create the driver
    driver = new_driver()

    # Open the login page
    driver.get(LOGIN_URL)

    # Wait until the username input is interactable
    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id_username" and @name="username"]')))
    password_input = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="id_password" and @name="password"]')))

    # Get the login data
    login_data = get_login_data()

    # Enter username and password
    username_input.send_keys(login_data[0])
    password_input.send_keys(login_data[1])

    # Click "Sign in" button
    sign_in_button = driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')
    sign_in_button.click()

    # Wait for login to complete
    time.sleep(5)