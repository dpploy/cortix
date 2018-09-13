import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cortix",
    version="0.0.1",
    author="Valmor F. de Almeida",
    author_email="Valmor_deAlmeida@uml.edu",
    description=" Cortix is a Python library for system-level\
                  module coupling, execution, and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dpploy.github.io/cortix",
    packages=['cortix', 'cortix.docs', 'cortix.examples',\
              'cortix.modulib.pyplot',\
              'cortix.src', 'cortix.support', 'cortix.tests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
