#this .py file is used to download a genric project structure for a specif project.
#to create a folder
import os
#to define a path for the creation of folder  
from pathlib import Path   
import logging

#if project is available then it will recreate else it will create a new one  
while True:
    project_name = input("Enter your project name: ")
    if project_name !='':
        break

logging.info(f"Creating project by name: {project_name}")

#this list creates the folder and files which we want to create.
#first it will ask project name and under that it will create dir and files
list_of_files = [
    ".github/workflows/.gitkeep",
    ".github/workflows/main.yaml",
    f"{project_name}/__init__.py",
    f"{project_name}/components/__init__.py",
    f"{project_name}/config/__init__.py",
    f"{project_name}/constant/__init__.py",
    f"{project_name}/entity/__init__.py",
    f"{project_name}/exception/__init__.py",
    f"{project_name}/logger/__init__.py",
    f"{project_name}/pipeline/__init__.py",
    f"{project_name}/utils/__init__.py",
    f"config/config.yaml",
    "schema.yaml",
    "requirements.txt",
    "setup.py",
    "main.py",
    "README.md"
]


for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)
    #if dir is not available, then create the dir and put all the files and folder
    if filedir !="":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating a new directory at : {filedir} for file: {filename}")
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating a new file: {filename} for path: {filepath}")
    else:
        logging.info(f"file is already present at: {filepath}")