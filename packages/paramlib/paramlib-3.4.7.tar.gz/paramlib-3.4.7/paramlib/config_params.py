#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 12:35:48 2024

@author: jonander

** DISCLAIMER **
This program serves as a module to store configuration data
like credentials, host info, etc.

*GLOBAL PARAMETERS MODULE STRUCTURE*

Programming Concepts
"""

#%% PROGRAMMING CONCEPTS

# Databases
DATABASE_CREDENTIALS = {
    "username": "username",
    "password": "cool-password",
    "host": "host",
    "port": "port",
    "database_name": "dbname"
}

DB_ERROR_CODE_DICT = {
    "1007": "Database already exists",
    "1045": "Wrong username",
    "1049": "Unknown database name",
    "1698": "Wrong password",
    "2003": "Wrong host name"
}

# JSON file path with registered information
USER_INFO_JSON_PATH = "users.json"
