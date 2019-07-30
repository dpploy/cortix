import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    req = fh.readlines()

setuptools.setup(
    name="cortix",
    version="1.0.2",
    author="Cortix Computing",
    author_email="tazzaoui@cs.uml.edu",
    description="Cortix is a Python library for system-level\
                module coupling, execution, and analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=req,
    url="https://cortix.org",
    packages=setuptools.find_namespace_packages(),
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
