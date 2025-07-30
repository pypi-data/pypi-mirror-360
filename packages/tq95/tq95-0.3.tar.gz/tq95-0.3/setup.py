from setuptools import setup

setup(
    name='tq95',
    version='0.3',  # bump the version every time you upload!
    py_modules=['launcher', 'flash'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'tq95 = launcher:main',
        ],
    },
    author='TechLabs Solutions',
    author_email='support@techlabs-solutions.com',
    description='TQ95 Utility: A lightweight command-line tool for system automation.',
    long_description=(
        'TQ95 is a simple Python-based utility designed for automation and scripting tasks.\n'
        'It includes a lightweight launcher that triggers the main functionality with ease.\n'
        'Ideal for internal workflows and testing environments.'
    ),
    long_description_content_type='text/plain',
    url='https://github.com/techlabs-solutions/tq95',
    project_urls={
        'Documentation': 'https://github.com/techlabs-solutions/tq95/wiki',
        'Source': 'https://github.com/techlabs-solutions/tq95',
        'Tracker': 'https://github.com/techlabs-solutions/tq95/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ],
    keywords='automation utility command-line',
    license='MIT',
    python_requires='>=3.6',
)
