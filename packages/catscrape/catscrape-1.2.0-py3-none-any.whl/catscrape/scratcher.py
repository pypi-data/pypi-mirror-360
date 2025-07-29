from .data import *
from .web import *

# SCRATCHER CLASS

class Scratcher(object):
    def __init__(self, username):
        self.username = username

        self.followers = None
        self.following = None

        self.about_me = None
        self.working_on = None

    @property
    def url(self):
        """
        Returns the URL of the user's profile.
        """
        return 'https://scratch.mit.edu/users/{}'.format(self.username)

    def _generate_followers_following_urls(self,
                                           n_pages: int,
                                           page_type: str=FOLLOWING
                                           ):
        # Generate the base url for the username page
        if page_type == FOLLOWERS:
            base_url = 'https://scratch.mit.edu/users/{}/followers/?page='.format(self.username)
        elif page_type == FOLLOWING:
            base_url = 'https://scratch.mit.edu/users/{}/following/?page='.format(self.username)
        else:
            raise Exception("Invalid page type: {}".format(page_type))
        
        # Initalize a list of urls
        urls = []

        # Iterate through all the pages of followers
        for i in range(n_pages):
            # Add the url to the list
            urls.append(base_url + str(i + 1))

        # Return the result
        return urls

    GET_FOLLOWERS_PAGES_TEXT = "page-links"
    GET_FOLLOWERS_PAGES_STOP_TEXT = "</div>"
    GET_FOLLOWERS_PAGES_SPAN = "span"
    GET_FOLLOWERS_PAGES_FIRST_SKIP = 42

    def _get_followers_pages(self,
                            page_type: str
                            ) -> int:
        """
        Returns the number of followers/following pages that the user has

        Parameters:
            page_type (str): Should be 'FOLLOWERS' or 'FOLLOWING'

        Returns:
            int: The number of followers/following pages
        
        """
        # Check if the data was previously saved
        if getattr(self, "followers_pages", None):
            return self.followers_pages
        
        # Generate the url for the first follower page
        url = self._generate_followers_following_urls(1, page_type)[0]

        # Get the HTML from the url
        html = get_website_html(url)

        # Find the location of the parent span tag of the list of links to other pages
        start_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_TEXT)

        # Add the skip amount to the start location
        start_location += Scratcher.GET_FOLLOWERS_PAGES_FIRST_SKIP

        # Cut off the html text from the start position so it is easier to work with
        html = html[start_location:]

        # Now, keep going till we find the stop text
        # The fomula is, count the "span"s, sub 2, and div 2
        span_count = 0

        while True:
            # Get the location of the next span
            span_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_SPAN)

            # Make sure we have not passed a div, if so, the pages section of the code has ended
            # After finding the div location, compare it to the location of the next span
            # If the div location is lower, the div is sooner than the next span and we break the loop
            div_location = html.find(Scratcher.GET_FOLLOWERS_PAGES_STOP_TEXT)
            if div_location < span_location:
                break

            # Otherwise, add one to the span count, and cut off the html
            span_count += 1
            html = html[span_location + len(Scratcher.GET_FOLLOWERS_PAGES_SPAN):]

        # Calculate the number of pages, based on the number of spans
        pages = int((span_count - 2) / 2)

        # 1 page will show up as 0, so set it
        if pages == 0:
            pages = 1

        # Save the data for later use
        self.followers_pages = pages

        # Return the number of pages
        return pages

    GET_FOLLOWERS_SKIP_CHAR = "/"
    GET_FOLLOWERS_CHARS_TO_SKIP = 20
    GET_FOLLOWERS_PER_PAGE = 59 # Doesn't include first username, the real number is 60
    GET_FOLLOWERS_AFTER_THUMB = 39
    GET_FOLLOWERS_THUMB_TEXT = "user thumb item"

    def _get_followers_following(self, page_type, search_for=None, verbose=True) -> list[str] | bool:
        # Generate the urls for the followers pages
        urls = self._generate_followers_following_urls(self._get_followers_pages(page_type), page_type)

        usernames = []

        for url in urls:
            # Print a progress message
            if verbose:
                print("Reading pages: {}/{}".format(urls.index(url) + 1, len(urls)))

            # Get the text
            html = get_website_html(url)

            # Return the existing usernames if the page failed to load
            if not html:
                return usernames

            # Get start location
            start_location = html.find(Scratcher.GET_FOLLOWERS_THUMB_TEXT) + Scratcher.GET_FOLLOWERS_AFTER_THUMB

            # Shorten url
            html = html[start_location - 1:]

            # Get first username
            usernames.append(html[:html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)])

            # First username needed one more char, so add it back
            html = html[1:]

            # Iterate through all the code
            for i in range(Scratcher.GET_FOLLOWERS_PER_PAGE):
                # Skip the number of triangles
                for i in range(Scratcher.GET_FOLLOWERS_CHARS_TO_SKIP):
                    start_location = html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)

                    # Cut off the html, but add delete one more char, this is the triangle
                    html = html[start_location + 1:]

                usernames.append(html[:html.find(Scratcher.GET_FOLLOWERS_SKIP_CHAR)])

            # Check if the username being searched for is in the list
            if search_for in usernames:
                return True
        
        # Each of the methods introduce some incorrect random text, delete that
        if page_type == FOLLOWERS:
            del usernames[-9:]
        elif page_type == FOLLOWING:
            del usernames[-14:]

        # Return the usernames. If searching for a username, return if the username was found
        if search_for:
            return search_for in usernames
        return usernames
    
    GET_DESC_START_TEXT = '<p class="overview">'
    GET_DESC_END_TEXT = '</p>'

    def _get_description(self, desc_type: str):
        assert desc_type in [ABOUT_ME, WORKING_ON], "Invalid description type: {}".format(desc_type)
        
        # Get the HTML of the user's profile
        html = get_website_html(self.url)

        # Repeat once for the 'About Me' and twice for the'Working On' section
        for i in range(1 if desc_type == ABOUT_ME else 2):
            # Find the overview section
            start_location = html.find(self.GET_DESC_START_TEXT)

            # Cutoff the HTML at the start location, and remove the start tag
            html = html[start_location + len(self.GET_DESC_START_TEXT):]

        # Find the end location
        end_location = html.find(self.GET_DESC_END_TEXT)

        # Cutoff the HTML at the end location
        html = html[:end_location]

        return html_lib.unescape(html)

    # Public methods

    def get_followers(self, verbose: bool=True) -> list[str]:
        """
        Return a list of the followers of the users.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            list[str]: The list of followers.
        """
        if self.followers:
            return self.followers
        
        # Get and cache
        followers = self._get_followers_following(page_type=FOLLOWERS, verbose=verbose)
        assert isinstance(followers, list)
        self.followers = followers

        return followers
    
    def get_following(self, verbose: bool=True) -> list[str]:
        """
        Return a list of the users that the user is following.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            list[str]: The list of users that the user follows.
        """
        if self.following:
            return self.following
        
        # Save and cache
        following = self._get_followers_following(page_type=FOLLOWING, verbose=verbose)
        assert isinstance(following, list)
        self.following = following
        
        return following
    
    def is_following(self, username, verbose: bool=True, cache: bool=True):
        """
        Returns whether the user is following the given username.

        Parameters:
            username (str): The username
            verbose (bool): Whether to be verbose.
            cache (bool): If true, the full result will be calculated, even if the name is found.
                If you intend to retrive the list of following later, this is useful.
                If this is the only time the following list of retrived, disabling this option will improve speed.

        Returns:
            bool: Whether the user is following the given username.
        """
        if self.following:
            return username in self.following
        if cache:
            self.following = self.get_following(verbose=verbose)
            return username in self.following
        else:
            return self._get_followers_following(page_type=FOLLOWING, search_for=username, verbose=verbose)
    
    def is_followed_by(self, username, verbose: bool=True, cache: bool=True):
        """
        Returns whether the user is followed by the given username.

        Parameters:
            username (str): The username
            verbose (bool): Whether to be verbose.
            cache (bool): If true, the full result will be calculated, even if the name is found.
                If you intend to retrive the list of following later, this is useful.
                If this is the only time the following list of retrived, disabling this option will improve speed.

        Returns:
            bool: Whether the user is followed by the given username.
        """
        if self.followers:
            return username in self.followers 
        if cache:
            self.followers = self.get_followers(verbose=verbose)
            return username in self.followers
        else:
            return self._get_followers_following(page_type=FOLLOWERS, search_for=username, verbose=verbose)
    
    
    def follower_count(self, verbose: bool=True):
        """
        Returns the number of followers of the user.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            int: The number of followers.
        """
        if self.followers:
            return len(self.followers)
        return len(self.get_followers(verbose=verbose))
    
    def following_count(self, verbose: bool=True):
        """
        Returns the number of users the user is following.

        Parameters:
            verbose (bool): Whether to be verbose.

        Returns:
            int: The following amount.
        """
        if self.following:
            return len(self.following)
        return len(self.get_following(verbose=verbose))
    

    def get_about_me(self):
        """
        Returns the 'About Me' section of the user's profile.

        Returns:
            str: The 'About Me' section of the user's profile.
        """
        if self.about_me:
            return self.about_me
        self.about_me = self._get_description(ABOUT_ME)
        return self.about_me
    
    def get_working_on(self):
        """
        Returns the 'Working On' section of the user's profile.

        Returns:
            str: The 'Working On' section of the user's profile.
        """
        if self.working_on:
            return self.working_on
        self.working_on = self._get_description(WORKING_ON)
        return self.working_on