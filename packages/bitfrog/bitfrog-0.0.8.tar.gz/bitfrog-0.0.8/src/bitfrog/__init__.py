"""
A Python API for Bitfrog notifications.
"""

import urllib.parse
import re
import requests
import logging

ENDPOINT = "https://bitfrog.dev/v1"

class ColoredFormatter(logging.Formatter):
        RESET = "\x1b[0m"
        COLORS = {
            logging.WARNING: "\x1b[33;20m",
            logging.ERROR: "\x1b[31;20m",
            logging.CRITICAL: "\x1b[31;20m",
            logging.INFO: "",
            logging.DEBUG: ""
        }

        def format(self, record):
            color = ""
            if(record.levelno in self.COLORS):
                color = self.COLORS[record.levelno]
            return color + super().format(record=record) + self.RESET

logger = logging.getLogger("Bitfrog")
formatter = ColoredFormatter('%(asctime)s - (%(name)s) [%(levelname)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

class TokenException(Exception):
    """A project token Exception"""

class ChannelException(Exception):
    """A channel Exception"""

class ProjectException(Exception):
    """A project exception."""

class NotificationException(Exception):
    """A project exception."""

class RateLimitException(Exception):
    """A project exception."""

def _response_handler(r: requests.Response):
    try:
        data = r.json()
        if("warning" in data):
            logger.warning(data["warning"])
    except: pass

def is_valid_token(token: str) -> bool:
    """
    Check if a tokens format is valid or not.

    >>> is_valid_token("a410-c45d-bce6-60af")
    True
    >>> is_valid_token("this is a token")
    False

    Args:
        token (str): The project token.
    
    Returns:
        bool: Whether the token is valid.
    """
    return re.fullmatch(r"^[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}$",
                        token) is not None

def ping(token: str = None, channel: str = None, timeout: requests.Timeout | None = None) -> bool:
    """Pings the server to check if it's responding.

    Args:
        token (str, optional): The token for the project you'd like to ping.
        channel (str, optional): The name of the channel you'd like to ping, 
                                 MUST be used with token.
        timeout (Timeout, optional): The timeout for the request.

    Returns:
        bool: Whether the server responds or not.
    """
    url = ENDPOINT + "/ping?"
    
    if(channel and not token):
        raise TokenException("You must provide a token when pinging a channel.")
    
    if(token):
        if not is_valid_token(token):
            raise TokenException("The token provided is not correctly formatted.")
        safe_token = urllib.parse.quote(token)
        url += f"token={safe_token}"
    
    if(channel):
        safe_channel = urllib.parse.quote(channel)
        url += f"&channel={safe_channel}"

    r = requests.get(url, timeout=timeout)
    _response_handler(r)

    return r.ok

def notify(message: str, token: str, title: str = None,
           channel: str = None, timeout: requests.Timeout | None = None) -> None:
    """
    Send a quick notification given a message and project token.

    *Its recomended to use `Project.notify()` or `Channel.notify()` instead.*

    Args:
        message (str): The message to send.
        token (str): The project token.
        title (str, optional): The title of the notification.
        channel (str, optional): The name of the channel to send to.
        timeout (Timeout, optional): The timeout for the request.
    """
    if not is_valid_token(token):
        raise TokenException("The token provided is not correctly formatted.")

    safe_message = urllib.parse.quote(message)
    safe_token = urllib.parse.quote(token)

    url = f"{ENDPOINT}/notify?token={safe_token}&message={safe_message}"
    
    if title is not None :
        safe_title = urllib.parse.quote(title)
        url += f"&title={safe_title}"

    if channel is not None:
        safe_channel = urllib.parse.quote(channel)
        url += f"&channel={safe_channel}"

    r = requests.get(url, timeout=timeout)
    _response_handler(r)

    if(not r.ok):
        if(r.status_code == 429):
            raise RateLimitException(r.text)
        try:
            error_code = r.json()["error"]
        except:
            error_code = "UNKNOWN"
        raise NotificationException(f"The notification failed to send. Error code: {error_code}")

class Channel:
    """
    A class representing a project channel.

    >>> channel = Channel("xxxx-xxxx-xxxx-xxxx", "Test Channel")
    >>> channel.notify("Hello World!")
    """
    def __init__(self, project_token: str, name: str, check=False):
        """
        Args:
            project_token (str): The project token.
            name (str): The channel name.
            check (bool): Whether to check if the channel exists.
        """
        if not is_valid_token(project_token):
            raise TokenException("The token provided is not correctly formatted.")

        self.project_token = project_token
        self.name = name

        if check and not ping(self.project_token, self.name):
            raise ChannelException("This channel does not exist.")

    def notify(self, message: str, title: str = None, timeout: requests.Timeout | None = None):
        """
        Send a notification to a channel.

        Args:
            message (str): The message to send.
            title (str, optional): The title of the notification.
            timeout (Timeout, optional): The timeout for the request.
        """
        notify(message, self.project_token, title=title, channel=self.name, timeout=timeout)

class Project:
    """
    A class representing a project.
    
    >>> project = Project("xxxx-xxxx-xxxx-xxxx")
    >>> project.notify("Hello World!") # Notifies the primary channel.
    
    """
    def __init__(self, token, check=False):
        """
        Args:
            token (str): The project token.
            check (bool): Whether to check if the project exists.
        """
        if not is_valid_token(token):
            raise TokenException("The token provided is not correctly formatted.")

        self.token = token

        if check and not ping(self.token):
            raise ProjectException("This project does not exist.")

    def channel(self, name: str, check=False) -> Channel:
        """
        Get a channel from a project.

        >>> channel = project.channel("Test Channel")
        >>> channel.notify("Hello World!")

        Args:
            name (str): The channel name.
            check (bool): Whether to check if the channel exists.
        
        Returns:
            Channel: The channel requested.
        """
        if check and not ping(self.token, name):
            raise ChannelException("This channel does not exist.")

        return Channel(self.token, name)

    def notify(self, message: str, title: str = None, channel: str = None,
               timeout: requests.Timeout | None = None):
        """
        Send a notification to a project.

        Args:
            message (str): The message to send.
            title (str, optional): The title of the notification.
            channel (str, optional): The name of the channel to send to.
            timeout (Timeout, optional): The timeout for the request.
        """
        notify(message, self.token, title=title, channel=channel, timeout=timeout)
