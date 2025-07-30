"""
TalkAbout - AI-Powered Object Query Proxy

A Python package that uses LLM intelligence to query and interact with objects
using natural language. Supply any object to the Proxy class and ask questions
about it in plain English - the AI will generate the appropriate Python code
to access or compute the requested information.
"""

__version__ = "0.1.2"
__author__ = "Denis Babochenko"
__email__ = "babochenko.denis2@gmail.com"
__description__ = "AI-powered object query proxy using Claude AI"

from .main import Talk

__all__ = ["Talk"]
