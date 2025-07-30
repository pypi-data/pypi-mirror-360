from .data import *
from .web import *

# STUDIO CLASS

class Studio(object):
    def __init__(self, studio_id: int):
        self.studio_id = studio_id

        self.curators = None
        self.followers = None

    @property
    def curator_page_url(self):
        return "https://scratch.mit.edu/studios/{}/curators".format(self.studio_id)
    
    @property
    def main_page_url(self):
        return "https://scratch.mit.edu/studios/{}/".format(self.studio_id)
    
    CHARS_AFTER_A_TO_SKIP = 16
    TAG_TO_FIND = "<a"
    START_LOCATION_TEXT = "studio-members-grid"
    ENDING_TEXT = "studio-member-tile"

    def _get_curators(self, scroll_wait_time: float | int, verbose: bool):
        # Create a new driver
        driver = new_driver()

        # Open the website
        driver.get(self.curator_page_url)

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
        start_location = find(html, Studio.START_LOCATION_TEXT)
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
            a_location = find(html, Studio.TAG_TO_FIND) + Studio.CHARS_AFTER_A_TO_SKIP

            # Cut off the html text to the "<a" tag
            html = html[a_location:]

            # Find the end of the username
            end_location = html.find("\"")

            # Add the username to the list
            curators.append(html[:end_location])

            # Find the next "<a" tag
            a_location = find(html, Studio.TAG_TO_FIND) + len(Studio.TAG_TO_FIND)

            # Cut off the HTML
            html = html[a_location:]

        return [curator.strip("/") for curator in curators]
    
    GET_FOLLOWERS_START_TEXT = ">"
    GET_FOLLOWERS_END_TEXT = "followers</span>"

    def _get_followers(self):
        # Get the HTML
        html = get_website_html(self.main_page_url)

        # Find the text just after the number of followers
        after_text_html = find(html, self.GET_FOLLOWERS_END_TEXT)

        # Cut off the HTML
        html = html[:after_text_html]

        # Find the start of the span tag
        start = find(html, ">")

        # Cut off the HTML
        html = html[start + 1:]

        return int(html.strip())
    
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

    def get_follower_count(self):
        """
        Return the number of followers the studio has.
        The only available information is the number of followers, not the usernames.
        
        Returns:
            int: The number of followers
        """
        if self.followers:
            return self.followers
        followers = self._get_followers()
        self.followers = followers
        return self.followers