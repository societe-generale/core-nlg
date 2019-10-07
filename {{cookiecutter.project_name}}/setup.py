# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import {{cookiecutter.project_name}}

setup(
    name="{{cookiecutter.project_name}}",
    version="0.0.1",
    description="",
    url="",
    author="",
    author_email="",
    license="",
    packages=find_packages(exclude=[]),
    include_package_data=True,
    cmdclass={"package": {{cookiecutter.project_name}}},
    zip_safe=False,
    install_requires=["CoreNLG",],
)
