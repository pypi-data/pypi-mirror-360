# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 23:43:46 2025

@author: DELL
"""

from setuptools import setup, find_packages

setup(
      author = "Aduragbemi Kinoshi",
      description= """A package that helps pull data from online xlsx files and googlesheets, after which it creates dataframes with each sheet.It also connects to flavors of SQL including SQLServer, MySQL, PostgreSQL, and DB browser.""",
      name = "pykinosh",
      version="0.1.1",
      packages = find_packages(include=["pykinosh","pykinosh.*"]),
      install_requires = ['pandas', 'sqlalchemy', 'psycopg2', "mysql-connector-python"],
      python_requires = '>=3.1')

