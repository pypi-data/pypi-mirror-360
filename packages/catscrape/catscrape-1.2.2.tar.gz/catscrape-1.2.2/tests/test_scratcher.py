from catscrape import Scratcher
import time

# TESTS

def test_scratcher_followers():
    # Get followers
    user = Scratcher("DominoKid11")
    followers = user.get_followers()

    print(followers)

    # Assertions
    assert len(followers) > 50
    assert "sparkbark" in followers

def test_scratcher_following():
    # Get following
    user = Scratcher("DominoKid11")
    following = user.get_following()

    print(following)

    # Assertions
    assert len(following) > 3
    assert "griffpatch" in following
    assert "WazzoTV" in following

def test_is_following():
    # Check is following
    user = Scratcher("DominoKid11")
    is_following = user.is_following("griffpatch")

    # Assertions
    assert is_following

def test_is_followed_by():
    # Check is followed by
    user = Scratcher("DominoKid11")

    # Someone might unfollow DominoKid11, so check two current followers
    is_followed_by = user.is_followed_by("Buckett15") or user.is_followed_by("Goos_kin")

    # Assertions
    assert is_followed_by

def test_description():
    # Get description
    user = Scratcher("griffpatch")
    description = user.get_about_me()
    description_working_on = user.get_working_on()

    assert "Got hooked on coding" in description
    assert "YouTube Tutorials" in description_working_on

def test_following_cache():
    # Get the following
    user = Scratcher("DominoKid11")
    user.get_following()

    # Run get_following again. It should return instantly
    start = time.time()
    user.get_following()
    total = time.time() - start

    # Assertions
    assert total < 0.2

def test_followers_cache():
    # Get the followers
    user = Scratcher("DominoKid11")
    user.get_followers()

    # Run get_followers again. It should return instantly
    start = time.time()
    user.get_followers()
    total = time.time() - start

    # Assertions
    assert total < 0.2