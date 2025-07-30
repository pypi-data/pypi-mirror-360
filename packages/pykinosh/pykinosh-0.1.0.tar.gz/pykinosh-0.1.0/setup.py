# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 23:43:46 2025

@author: DELL
"""

from setuptools import setup, find_packages

setup(
      author = "Aduragbemi Kinoshi",
      description= """A package that helps pull daat from online xlsx and googlesheets.
      It also connects to flavors of SQL including SQLServer, MySQL, PostgreSQL, and DB browser.""",
      name = "pykinosh",
      version="0.1.0",
      packages = find_packages(include=["pykinosh","pykinosh.*"]),
      install_requires = ['pandas'],
      python_requires = '>=3.1')

