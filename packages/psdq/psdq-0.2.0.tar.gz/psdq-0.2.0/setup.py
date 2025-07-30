from setuptools import find_packages, setup

setup(
    name='psdq',
    packages=find_packages(),
    version='0.2.0',
    description='Ad Hoc Data Quality Tool for PySpark',
    author='Alexandre "Alex" de Magalhaes',
    author_email="alexandredemagalhaess@gmail.com",
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=4.4.1'],
    test_suite='tests',
)
