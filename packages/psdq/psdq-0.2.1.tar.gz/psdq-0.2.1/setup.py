from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='psdq',
    packages=find_packages(),
    version='0.2.1',
    description='Ad Hoc Data Quality Tool for PySpark',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Alexandre "Alex" de Magalhaes',
    author_email="alexandredemagalhaess@gmail.com",
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=4.4.1'],
    test_suite='tests',
)
