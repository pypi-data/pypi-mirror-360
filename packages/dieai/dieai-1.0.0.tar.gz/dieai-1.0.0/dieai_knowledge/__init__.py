"""
DieAI - Python Library for AI Chatbots and Projects
A comprehensive AI library similar to OpenAI's API for building intelligent applications.
"""

__version__ = "1.0.0"
__author__ = "DieAI Team"
__email__ = "info@dieai.com"

from .client import DieAI
from .knowledge_base import KnowledgeBase
from .math_solver import MathSolver
from .science_facts import ScienceFacts
from .unit_converter import UnitConverter
from .chatbot import ChatBot, AIRobot, ConversationAnalyzer

__all__ = [
    'DieAI',
    'ChatBot',
    'AIRobot',
    'ConversationAnalyzer',
    'KnowledgeBase',
    'MathSolver', 
    'ScienceFacts',
    'UnitConverter'
]