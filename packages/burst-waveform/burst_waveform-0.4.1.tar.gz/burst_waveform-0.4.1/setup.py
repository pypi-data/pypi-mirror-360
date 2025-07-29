import os
from setuptools import setup
from setuptools import find_packages

requires = []
install_requires = [
    "numpy",
    "gwpy"
]


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_files(dirname, relpath=None):
    def find_paths(dirname):
        items = []
        for fname in os.listdir(dirname):
            path = os.path.join(dirname, fname)
            if os.path.isdir(path):
                items += find_paths(path)
            elif not path.endswith(".py") and not path.endswith(".pyc"):
                items.append(path)
        return items

    items = find_paths(dirname)
    if relpath is None:
        relpath = dirname
    print(items)
    return [os.path.relpath(path, relpath) for path in items]


extensions = [
]


setup(
    name="cWB Burst Waveform",
    author="Yumeng Xu",
    author_email="yumeng.xu@ligo.org",
    description=("python waveform model for cWB burst waveforms"),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    keywords=['ligo', 'physics', 'gravity', 'signal processing', 'gravitational waves'],
    url="https://git.ligo.org/yumeng.xu/setup.py",
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    # ext_modules=cythonize(extensions),
    python_requires='>=3.8'
)