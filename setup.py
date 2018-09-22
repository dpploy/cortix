import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cortix",
    version="0.0.4",
    author="Valmor F. de Almeida",
    author_email="Valmor_deAlmeida@uml.edu",
    description=" Cortix is a Python library for system-level\
                  module coupling, execution, and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://github.com/dpploy/cortix",
    packages=['cortix', 'cortix.docs', 'cortix.examples',
              'cortix.examples.modulib', 'cortix.examples.main',
              'cortix.examples.input', 'cortix.examples.modulib.droplet',\
              'cortix.modulib.pyplot','cortix.src',\
              'cortix.src.utils', 'cortix.support', 'cortix.tests',
              'cortix.tests.input'],
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
