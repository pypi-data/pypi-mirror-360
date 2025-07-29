# Catscrape

*Catscrape* is a library with web scraping functions for the popular beginner programming website Scratch.mit.edu. It can extract data from followers, studios, and *soon* extract hearts, stars, and remix counts for projects.

## Functionality

This library is new, so most features are on the to-do list. Here are the supported and planned features:

|Data to Extract|Support|
|--|--|
|User followers|✅Supported|
|User following|✅Supported|
|Get user "About Me"|✅Supported|
|Get user "What I'm Working On"|✅Supported|
|Get user shared projects|🟨Coming Soon|
|Studio curators|✅Supported|
|Auto invite to studio|✅Supported|
|Project hearts|✅Supported|
|Project stars|✅Supported|
|Project remixes|✅Supported|
|Project viewes|✅Supported|
|Get project description|🟨Coming Soon|
|Get project notes|🟨Coming Soon|
|Get sprite names|🟨Coming Soon|
|Get comments|🟨Coming Soon|
|Anything else|🟥Not Supported|

## Installation

The library can be installed via `pip install`:
```bash
pip install catscrape
```
The install might take some time as the dependencies include Selenium

# Documentation

## Scratcher

The `Scratcher` class has methods to get the number of followers and the number of users the user is following. They are all listed below.
A `Scratcher` object can be initalized as shown below. In the example code, it is assumed a variable named `user` is assigned to a `Scratcher` object.
```python
>>> import catscrape
>>> user = catscrape.Scratcher("CrystalKeeper7")
```
All of the methods can be passed a `verbose` argument, which controls various print statements to assure the user of progress.

All of the methods cache their outputs. For example, if `Scratcher.follower_count` is called, then `Scratcher.get_followers` will return instantly.
`Scratcher.follower_count` and `Scratcher.get_followers` all cache their outputs for each other (as well as their following inverses); `Scratcher.is_following` (and it's `is_followed_by` inverse) *can* also cache it's output, if the `cache` argument is set to `True`. If you intend to call other methods after the `is_following` function, make sure the `cache` parameter is set to `True`. If you only intend to call `is_following` once, set the `cache` parameter to `False`.
The `get_about_me` and `get_working_on` methods also cache their outputs.

### `get_followers`

The `Scratcher.get_followers` method returns a list of the the followers of the user:
```python
>>> followers = user.get_followers()
>>> type(followers)
<class 'list'>
>>> type(followers[0])
<class 'str'>
```

### `get_following`

The `Scratcher.get_following` method returns a list of the users that the user is following:
```python
>>> following = user.get_following()
>>> type(followers)
<class 'list'>
>>> type(followers[0])
<class 'str'>
```

### `is_following`

The `Scratcher.is_following` method has a parameter `username`, and returns whether the user is following that username.
```python
>>> is_following_griffpatch = user.is_following("griffpatch")
>>> type(is_following_griffpatch)
<class 'bool'>
```

### `is_followed_by`

The inverse of the `Scratcher.is_following` method, returning whether the user is followed by the given username.
```python
>>> is_following_griffpatch = user.is_following("griffpatch")
>>> type(is_following_griffpatch)
<class 'bool'>
```

### `follower_count` and `following_count`

Returns the follower or following count for the user.
```python
>>> num_followers = user.follower_count()
>>> type(num_followers)
<class 'int'>
>>> num_followers = user.follower_count()
>>> type(num_followers)
<class 'int'>
```

### `get_about_me` and `get_working_on`

Returns the text of the "About Me" or "What I'm Working On" section of the user's page.
```python
>>> about_me = user.get_about_me()
>>> type(about_me)
<class 'str'>
>>> working_on = user.get_working_on()
>>> type(working_on)
<class 'str'>
```

## Providing Login

The `Studio.invite_curators` method requires an account with manager or host authority to invite curators. The `save_login_data` function saves the login data of an account. The data is saved in a pickle file in a folder in the appdata folder of the computer. Example usage is shown below:
```python
>>> from catscrape import save_login_data
>>> save_login_data("<username>", "<password>")
Successfully saved the login data.
```
## Studio

The `Studio` class has methods to get the curators of the studio, and to auto-invite curators. Below is an example of initalizing the studio class. The one parameter is the studio id.
```python
>>> from catscrape import Studio
>>> studio = Studio(45693845)
```

The `Studio.get_curators` and `Studio.curator_count` methods both cache their outputs and use each others cache.

### `get_curators`

The `Studio.get_curators` method returns all of the curators of the studio. Becuase it has to physically scroll through the curators using selenium (headless, of course), this function tends to take longer. The `scroll_wait_time` parameter adjusts the amount of time to wait after pressing the "Load More" button to press it again. Changing this too low causes instability in results, possibly leading to incorrect results, with too few curators.
```python
>>> curators = studio.get_curators(
...     scroll_wait_time=0.25 # More reliable, but slower
... )
>>> type(curators)
<class 'list'>
>>> type(curators[0])
<class 'str'>
```

### `curator_count`

The `Studio.curator_count` method returns the number of curators in the studio.
```python
>>> num_curators = studio.curator_count()
>>> type(num_curators)
<class 'int'>
```

### `invite_curators`

The `Studio.invite_curators` method invites curators to the studio. Login info is required for this. See "Providing Login" above.
The usernames to invite should be passed to the method. A physical Chrome window will open, and will be controlled by selenium to login and invite the curators.
Warning: I have experienced failure to invite more users after about 100-150 invites in a row. Try to limit the number of usernames to invite in a batch to below this value to avoid partial failure.
```python
>>> invitees = ["griffpatch", "CrystalKeeper7", "DominoKid11", "username4"]
>>> studio.invite_curators(
...     usernames=invitees
... )
<invites curators>
```

# Versions

## 1.2.2
- Hotfix: Fixed invalid `def` syntax in `project.py`
## 1.2.1
- Removed the `Studio.invite_curators` method for simplification, and to stay focused on *catscrape*'s objective.
## 1.2.0
- Added the `Project` class.
- Revamped caching of data in `Scratcher` class, and added caching in `Studio` class.
- Added the `Studio.curator_count` method.
- Made the Selenium driver run with a disguised agent name, reducing chance of auto-block.
- Added unit tests to the Github repository.
## 1.1.2
- Hotfix: Incorrect `import` statements in `scratcher.py` and `web.py`.
## 1.1.1
- Added methods to get user "About Me" and "What I'm Working On" sections.
## 1.1.0
- Initial release