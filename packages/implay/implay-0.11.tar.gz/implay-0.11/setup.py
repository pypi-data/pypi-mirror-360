from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='implay',
    version='0.11',
    author='subin erattakulangara',
    url='https://subinek.com/',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'ipywidgets',
        'opencv-python',
        'IPython',
        'numpy'
    ]
)