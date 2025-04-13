import os
import re
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
import subprocess

# Function to load dependencies from requirements.txt
def load_requirements(filename="requirements.txt"):
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]

# Function to read __version__ from __init__.py
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'jsonl2html', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string in __init__.py.")

# Custom build command to run tests before building
class BuildWithTests(_build_py):
    def run(self):
        # Run pytest before build
        result = subprocess.run(['pytest', '--maxfail=1', '--disable-warnings'], check=False)
        if result.returncode != 0:
            raise RuntimeError("Tests failed; aborting build.")
        else:
            print("Tests succeeded; continuing build.")
        super().run()

setup(
    name='jsonl2html',
    version=get_version(),
    packages=find_packages(),
    install_requires=load_requirements(),  # Load dependencies from requirements.txt
    entry_points={
        'console_scripts': [
            'jsonl2html=jsonl2html.convert:main_bash_entry_point',  # Temporarily test with this script
        ],
    },
    package_data={
        'jsonl2html': ['html_template.html'],  # Include your HTML template in the package
    },
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    description='A tool to convert JSONL to HTML',
    author='Adamenko Pavel',
    author_email='padamenko@gmail.com',
    cmdclass={
        'build_py': BuildWithTests,  # Custom command to run tests before building
    },
)
