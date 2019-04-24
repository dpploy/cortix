import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    req = fh.readlines()

setuptools.setup(
    name="cortix",
    version="0.1.7",
    author="Cortix Computing",
    author_email="valmor_dealmeida@uml.edu",
    description=" Cortix is a Python library for system-level\
                  module coupling, execution, and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=req,
    url="https://cortix.org",
    packages=['cortix', 'cortix.docs', 'cortix.examples',
              'cortix.examples.modulib', 'cortix.examples.console_run',
              'cortix.examples.notebook_run',
              'cortix.examples.input', 'cortix.examples.modulib.droplet',\
              'cortix.modulib.pyplot','cortix.src',\
              'cortix.src.utils', 'cortix.support', 'cortix.tests',
              'cortix.tests.input', 'cortix.examples.modulib.wind'],
    keywords = ['simulation', 'math'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Topic :: Scientific/Engineering :: Mathematics',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Topic :: Education',
        'Topic :: Utilities'
    ],
)
