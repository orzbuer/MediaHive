from setuptools import setup, find_packages

setup(
    name='mediahive',
    version='0.1.0',
    description='A multi-source movie metadata scraper and media organizer',
    author='orzbuer',
    url='https://github.com/orzbuer/MediaHive',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.28.0',
        'lxml>=4.9.0',
        'Pillow>=9.0.0',
        'tqdm>=4.60.0',
    ],
    entry_points={
        'console_scripts': [
            'mediahive=cinemeta:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
