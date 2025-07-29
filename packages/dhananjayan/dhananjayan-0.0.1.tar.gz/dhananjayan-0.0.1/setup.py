from setuptools import find_packages, setup

setup(
    name="dhananjayan",
    packages= find_packages(include=["pydhan"]), 
    version="0.0.1",
    description="Returns dot product along with time taken for computing it",
    author="Dhananjayan Sudhakar",
    author_email="vvandhiyadhevan@gmail.com",
    install_requires= [],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)