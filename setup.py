# -*- coding: utf-8 -*-
"""
created on 20/12/2018 16:37
@author: fgiely
"""

from setuptools import setup, find_packages
import CoreNLG

setup(
    name="CoreNLG",
    version="1.0.0",
    description="",
    url="https://github.com/societe-generale/core-nlg.git",
    author="Fabien Giely",
    license="Apache v2",
    packages=find_packages(exclude=["*.logs"]),
    include_package_data=True,
    cmdclass={"package": CoreNLG},
    zip_safe=False,
    install_requires=["lxml"],
)
