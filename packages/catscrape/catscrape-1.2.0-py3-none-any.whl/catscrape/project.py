from .web import *
from .data import *

# PROJECT CLASS

class Project:
    def __init__(self, id_: int):
        self.id = id_

        self.hearts = None
        self.stars = None
        self.remix = None
        self.views = None

    @property
    def url(self):
        return f"https://scratch.mit.edu/projects/{self.id}/"
    
    # Get stat
    
    GET_STAT_CLOSING_TEXT = "</div>"

    def _get_stat(self, stat):
        # Get the HTML
        html = get_website_html(self.url, use_java=True)

        # Find the stat text
        stat_loc = html.find(stat)
        assert stat_loc != -1

        # Cut off the HTML
        html = html[stat_loc + len(stat):]

        # Find the closing text
        closing_text = html.find(self.GET_STAT_CLOSING_TEXT)
        assert stat_loc != -1

        # Cut off the end of the HTML
        html = html[:closing_text]

        # Return the number
        return int(html)

    # Public methods

    HEART_STAT_NAME = '<div class="project-loves">'
    STAR_STAT_NAME  = '<div class="project-favorites">'
    REMIX_STAT_NAME = '<div class="project-remixes">'
    VIEWS_STAT_NAME = '<div class="project-views">'

    def get_hearts(self):
        """
        Returns the number of hearts the project has

        Returns:
            int: The number of hearts
        """
        if self.hearts:
            return self.hearts
        return self._get_stat(self.HEART_STAT_NAME)
    
    def get_stars(self):
        """
        Returns the number of stars the project has

        Returns:
            int: The number of stars
        """
        if self.stars:
            return self.stars
        return self._get_stat(self.STAR_STAT_NAME)

    def get_remixes(self):
        """
        Returns the number of remixes the project has

        Returns:
            int: The number of remixes
        """
        if self.remix:
            return self.remix
        return self._get_stat(self.REMIX_STAT_NAME)

    def get_views(self):
        """
        Returns the number of views the project has

        Returns:
            int: The number of views
        """
        if self.views:
            return self.views
        return self._get_stat(self.VIEWS_STAT_NAME)