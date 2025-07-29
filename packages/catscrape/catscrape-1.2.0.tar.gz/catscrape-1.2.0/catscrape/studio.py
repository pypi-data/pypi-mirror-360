from .data import *
from .web import *

# STUDIO CLASS

class Studio(object):
    def __init__(self, studio_id: int):
        self.studio_id = studio_id

        self.curators = None

    def _get_curator_url(self):
        return "https://scratch.mit.edu/studios/{}/curators".format(self.studio_id)
    
    CHARS_AFTER_A_TO_SKIP = 16
    TAG_TO_FIND = "<a"
    START_LOCATION_TEXT = "studio-members-grid"
    ENDING_TEXT = "studio-member-tile"

    def _get_curators(self, scroll_wait_time: float | int, verbose: bool):
        # Create a new driver
        driver = new_driver()

        # Get the url of the studio
        url = self._get_curator_url()

        # Open the website
        driver.get(url)

        # Scroll through the curators
        wait = WebDriverWait(driver, 5)
        i = 0
        while True:
            time.sleep(scroll_wait_time)

            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="button"]')))
                button.click()
            except:
                break

            i += 1
            if verbose:
                print(f"Reading page: {i}")

        # Copy the HTML text
        html = driver.page_source[:]

        # Find all the curators:
        # First, find the "studio-members-grid" as the start location
        # Then, find each of the "<a" tags, and skip 16 chars to get the username
        # Cut off the html, and find the first " symbol as the end of the username
        # Add the username to the list
        # Skip one "<a" tag, and repeat the process

        # Cut off the html text to the start location
        start_location = html.find(Studio.START_LOCATION_TEXT)
        html = html[start_location:]

        # Close the driver as it is no longer needed
        driver.quit()

        curators = []
        while True:
            # Try to find the "studio-member-tile" text
            # If it is not found, we are done
            if html.find(Studio.ENDING_TEXT) == -1:
                break

            # Find the first "<a" tag
            a_location = html.find(Studio.TAG_TO_FIND) + Studio.CHARS_AFTER_A_TO_SKIP

            # Cut off the html text to the "<a" tag
            html = html[a_location:]

            # Find the end of the username
            end_location = html.find("\"")

            # Add the username to the list
            curators.append(html[:end_location])

            # Find the next "<a" tag
            a_location = html.find(Studio.TAG_TO_FIND) + len(Studio.TAG_TO_FIND)

            # Cut off the HTML
            html = html[a_location:]

        return [curator.strip("/") for curator in curators]
    
    # Public methods

    def get_curators(self, scroll_wait_time: float | int=0.2, verbose: bool=True):
        """
        Returns a list of the curators and managers.
        
        Parameters:
            scroll_wait_time (float | int): Controls the amount of time to wait after clicking the "Load More"
            button the click the next "Load More" button. If too low, the driver may exhibit unexpected behavior
            and give an incomplete list of curators.
            verbose: Whether to be verbose
            
        Returns:
            list: A list of the curators (plus managers and host) of the studio.
        """
        if self.curators:
            return self.curators
        curators = self._get_curators(scroll_wait_time=scroll_wait_time, verbose=verbose)
        self.curators = curators
        return curators
    
    def curator_count(self, scroll_wait_time: float | int=0.2, verbose: bool=True):
        """
        Returns the number of curators in the studio. The result *will* be cached.
        
        Parameters:
            scroll_wait_time (float | int): Controls the amount of time to wait after clicking the "Load More"
            button the click the next "Load More" button. If too low, the driver may exhibit unexpected behavior
            and give an incomplete list of curators.
            verbose: Whether to be verbose

        Returns:
            int: The number of curators
        """
        return len(self.get_curators(scroll_wait_time=scroll_wait_time, verbose=verbose))

    def invite_curators(self, usernames:list):
        """
        Invite the given list of usernames to the studio.
        Note: This action requires a Scratch account with manager permissions or above.
            To provide the login data, run `catscrape.save_login_data` with the username and password passed.
        Note: Don't try to give more than 100-150 usernames, as the Scratch server will occasionally stop allowing invites.

        WARNING: Spamming invites can get your scratch account blocked or banned!
        
        Parameters:
            usernames (list): The list of usernames to invite
        """
        # Check if the list of usernames is large
        if len(usernames) > 100:
            warnings.warn(f"You passed {len(usernames)} usernames. With this many, the Scratch server might stop responding to invites, and invite only some of the curators. You also might get your account blocked.")

        # Create a new driver
        driver = new_driver(headless=False)

        # Initalize the wait object
        wait = WebDriverWait(driver, 5)

        # Login to the account
        login()

        # Go to the URL of the studio
        driver.get(self._get_curator_url())

        for username_idx, username in enumerate(usernames):
            # Wait until the element is interactive
            invite_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[not(@name="q")]')))
            
            # Type the username
            invite_input.send_keys(username)

            # Press the [ENTER] key
            invite_input.send_keys(Keys.RETURN)

            time.sleep(0.3)

        # Close the browser
        driver.quit()