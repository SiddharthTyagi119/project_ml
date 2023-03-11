##to define the version of a library.to release any app as a package we have to push a new version of our
# project after making any new  changes 
#in it
from setuptools import setup, find_packages
from typing import List

PROJECT_NAME = "Machine Learning project"
VERSION = "0.0.1"
AUTHOR = "Shivan Kumar"
DESCRIPTION = "This is our Machine learning project"

REQUIREMENT_FILE_NAME = "requirements.txt"

HYPHEN_E_DOT = "-e ."


def get_requirements_list() -> List[str]:
    with open(REQUIREMENT_FILE_NAME) as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list



setup(
    name = PROJECT_NAME,
    version = VERSION,
    author = AUTHOR,
    description=DESCRIPTION,
    #find package-> it will find main init file under main project
    packages= find_packages(),
    install_requires = get_requirements_list()
)