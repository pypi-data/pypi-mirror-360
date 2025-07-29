#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Jun  9 12:14:15 2022

@author: jonander

** DISCLAIMER **
This program serves as a module to store parameters that are used frequently or globally.

*GLOBAL PARAMETERS MODULE STRUCTURE*

1. Time-Related Parameters
2. Mathematical Concepts
3. Programming Concepts
4. Socio-Economical Concepts

All constant names in this module are in uppercase following Python naming conventions.
"""

#%% 1. TIME-RELATED PARAMETERS

#------#
# Time #
#------#

# Basic time format strings
BASIC_TIME_FORMAT_STRS = {
    "H": "%F %T",
    "H_NO_DATE_SEP": "%Y%m%d %T",
    "D": "%F",
    "D_NO_DATE_SEP": "%Y%m%d",
    "M": "%Y-%m",
    "Y": "%Y"
}

# Non-standard time format strings
NON_STANDARD_TIME_FORMAT_STRS = {
    "CTIME_H": "%a %b %d %T %Y",
    "CTIME_D": "%a %b %d %Y",
    "CTIME_M": "%b %Y"
}

# Custom time format strings
CUSTOM_TIME_FORMAT_STRS = {
    "CT_EXCEL_SPANISH_H": "%d/%m/%y %T",
    "CT_EXCEL_SPANISH_NO_BAR_H": "%d%m%y %T",
    "CT_EXCEL_SPANISH_D": "%d/%m/%y",
    "CT_EXCEL_SPANISH_NO_BAR_D": "%d%m%y"
}

# Month number to letter mapping
MONTH_NUMBER_DICT = {
    1: "J",
    2: "F",
    3: "M",
    4: "A",
    5: "M",
    6: "J",
    7: "J",
    8: "A",
    9: "S",
    10: "O",
    11: "N",
    12: "D"
}

# Seasonal time frequency dictionary
SEASON_TIME_FREQ_DICT = {
    1: "Q-JAN",
    2: "Q-FEB",
    3: "Q-MAR",
    4: "Q-APR",
    5: "Q-MAY",
    6: "Q-JUN",
    7: "Q-JUL",
    8: "Q-AUG",
    9: "Q-SEP",
    10: "Q-OCT",
    11: "Q-NOV",
    12: "Q-DEC"
}

# Mathematical approximation for year length
MATHEMATICAL_YEAR_DAYS = 360

# Time frequencies
TIME_FREQUENCIES_COMPLETE = ["year", "season", "month", "day", "hour", "minute", "second"]
TIME_FREQUENCIES_ABBREVIATED = ["yearly", "seasonal", "monthly", "daily", "hourly"]
TIME_FREQUENCIES_BRIEF = ["year", "seas", "mon", "day", "hour"]

# Supported date units
PANDAS_DATE_UNIT_LIST = ['D', 'ms', 'ns', 's', 'us']
NUMPY_DATE_UNIT_LIST = ['Y', 'M', 'D', 'h', 'm', 's', 'ms', 'us', 'ns']

UNIT_FACTOR_DICT = {
    "D": 1000,
    "s": 1,
    "ms": 1e-3,
    "us": 1e-6,
    "ns": 1e-9
}

#%% 2. MATHEMATICAL CONCEPTS

# Basic operators
BASIC_ARITHMETIC_OPERATORS = ["+", "-", "*", "/"]

# Set algebra
SET_OPERATIONS = [
    "union", "difference", "intersection", 
    "symmetric_difference", "comparison"
]

#%% 3. PROGRAMMING CONCEPTS

# Operative Systems
FILESYSTEM_CONTEXT_MODULES = ["os", "Path", "shutil", "subprocess"]  # 'Path' from 'pathlib' module
STORAGE_ENTITY_TYPES = ["file", "directory"]

# Regular expressions
PASSWORD_REGEX_PATTERN = r"^(?=.{8,})(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_\W]).+$"

# Strings
COMMON_DELIMITER_LIST = ["_", "-", ";", ":", ",", "\n", "\t", " "]

#%% 4. SOCIO-ECONOMICAL CONCEPTS

# Climate change
EMISSION_RCP_SCENARIOS = ["historical", "rcp26", "rcp45", "rcp85"]
CLIMATE_FILE_EXTENSIONS = ["nc", "grib", "netcdf_zip", "csv"]
