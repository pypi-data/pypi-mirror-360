"""
tfq0seo - Professional SEO Analysis Toolkit
Open source alternative to Screaming Frog SEO Spider
"""

__version__ = "2.1.3"
__author__ = "tfq0"

from .core.app import SEOAnalyzerApp
from .core.crawler import WebCrawler
from .analyzers.seo import SEOAnalyzer
from .exporters.base import ExportManager

__all__ = [
    "SEOAnalyzerApp",
    "WebCrawler", 
    "SEOAnalyzer",
    "ExportManager"
] 


