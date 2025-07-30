from setuptools import setup, find_packages

setup(
    name="test-require-weiwei",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    tests_require=[
        "pytest",
        "requests @ git+https://github.com/psf/requests.git@v2.31.0#egg=requests"
    ],
    test_suite="tests"
)
