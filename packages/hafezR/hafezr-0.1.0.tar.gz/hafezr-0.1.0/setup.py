from setuptools import setup, find_packages

setup(
    name="hafezR",
    version="0.1.0",
    description="Setup script to install GCC and configure R Makevars for the hafez package.",
    author="Your Name",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hafezR=hafez.install_deps:install_dependencies',
        ],
    },
    install_requires=[],
    python_requires='>=3.6',
)

