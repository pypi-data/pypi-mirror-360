import shutil
import os
import pathlib
from distutils.dir_util import copy_tree

def copy_html_files():
    from_directory = f'{pathlib.Path(__file__).parent.resolve()}/files_to_copy_into_user'
    to_directory = f'{os.getcwd()}/views'

    copy_tree(from_directory, to_directory)
    print(f"Copied views. They are available at views directory!")


def copy_flask_server():
    original = f'{pathlib.Path(__file__).parent.resolve()}/files_to_copy_into_user/app.py'
    target = f'{os.getcwd()}/app.py'
    shutil.copyfile(original, target)
    print(f"Copied flask server from library!")


def copy_services_directory():
    from_directory = f'{pathlib.Path(__file__).parent.resolve()}/services'
    to_directory = f'{os.getcwd()}'

    copy_tree(from_directory, to_directory)
    print(f"Copied services. They are available at services directory! Do not delete (otherwise it will break code server). Feel free to experiment!")
