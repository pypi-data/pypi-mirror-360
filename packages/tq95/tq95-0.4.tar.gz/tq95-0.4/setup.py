from setuptools import setup

setup(
    name='tq95',
    version='0.4',  # bump version
    py_modules=['launcher', 'tq95'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'tq95 = launcher:main',
        ],
    },
    author='TechLabs Solutions',
    author_email='support@techlabs-solutions.com',
    description='TQ95 Utility: A lightweight command-line tool for system automation.',
    long_description='TQ95 is a simple Python utility with a launcher and main module.',
    long_description_content_type='text/plain',
    url='https://github.com/techlabs-solutions/tq95',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
