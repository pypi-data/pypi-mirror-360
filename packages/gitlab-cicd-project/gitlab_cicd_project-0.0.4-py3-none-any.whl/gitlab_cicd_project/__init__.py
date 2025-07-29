#the whole directory will act as a package
# gitlab_cicd_project/__init__.py

"""
LDMS WiFi Speed Test Package

An interactive WiFi speed testing application with real-time plotting,
network information display, and snapshot capabilities.
"""

from .main import hello, WifiSpeedTester

__version__ = "0.1.0"
__author__ = "Shreyas Prabhakar"
__email__ = "shreyas.prabhakar97@gmail.com"

# Make main functions easily accessible
__all__ = ['hello', 'WifiSpeedTester']

