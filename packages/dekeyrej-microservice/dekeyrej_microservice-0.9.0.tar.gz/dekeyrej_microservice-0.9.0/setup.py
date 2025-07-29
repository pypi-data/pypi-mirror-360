from setuptools import find_packages, setup

setup(
    name='dekeyrej-microservice',
    packages=find_packages(include=['dekeyrej-microservice']),
    version='0.9.0',
    description='Matrix Microservice superclass',
    author='J.DeKeyrel',
    license='MIT',
    install_requires=['arrow','requests', 'redis'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)