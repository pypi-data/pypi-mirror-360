from catscrape import Project

# VARIABLES

TEST_PROJECT_ID = 948573479

# TESTS

def test_get_hearts():
    # Get the hearts
    project = Project(TEST_PROJECT_ID)
    hearts = project.get_stars()

    # Assertions
    assert hearts > 1000
    assert hearts < 1000000

def test_get_stars():
    # Get the stars
    project = Project(TEST_PROJECT_ID)
    stars = project.get_stars()

    # Assertions
    assert stars > 1000
    assert stars < 1000000

def test_get_remixs():
    # Get the remixes
    project = Project(TEST_PROJECT_ID)
    remixes = project.get_remixes()

    # Assertions
    assert remixes > 1000

def test_get_views():
    # Get the views
    project = Project(TEST_PROJECT_ID)
    views = project.get_views()

    # Assertions
    assert views > 100000