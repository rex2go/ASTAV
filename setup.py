from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Advanced Survey Tools And Validation'

# Setting up
setup(
    name="astav",
    version=VERSION,
    author="Tim Hübert",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)