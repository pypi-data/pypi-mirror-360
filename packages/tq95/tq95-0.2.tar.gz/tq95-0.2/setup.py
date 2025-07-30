from setuptools import setup

setup(
    name='tq95',
    version='0.2',
    py_modules=['launcher', 'flash'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'tq95 = launcher:main',
        ],
    },
)
