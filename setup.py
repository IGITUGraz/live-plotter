"""
This file installs the ltl package.
Note that it does not perform any installation of the documentation. For this, follow the specified procedure in the
 README
"""

from setuptools import setup
import re


def get_requirements(filename):
    """
    Helper function to read the list of requirements from a file
    """
    dependency_links = []
    with open(filename) as requirements_file:
        requirements = requirements_file.read().strip('\n').splitlines()
    for i, req in enumerate(requirements):
        if ':' in req:
            match_obj = re.match(r"git\+(?:https|ssh|http):.*#egg=(\w+)-(.*)", req)
            assert match_obj, "Cannot make sence of url {}".format(req)
            requirements[i] = "{req}=={ver}".format(req=match_obj.group(1), ver=match_obj.group(2))
            dependency_links.append(req)
    return requirements, dependency_links


requirements, dependency_links = get_requirements('requirements.txt')
setup(
    name="Realtime Plotter",
    version="0.1.0",
    packages=['realtimeplotter'],
    author="Anand Subramoney",
    author_email="anand@igi.tugraz.at",
    description="This module provides the library to do realtime plotting with matplotlib",
    install_requires=requirements,
    provides=['realtimeplotter'],
    dependency_links=dependency_links,
)
