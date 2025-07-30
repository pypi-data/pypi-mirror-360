from setuptools import setup
from pathlib import Path

long_description = (Path(__file__).parent / 'README.md').read_text()
setup(
    name='lilliepy-rebound',
    version='0.0.1',
    install_requires=[
        'reactpy',
        'asyncio'
    ],
    packages=["lilliepy_rebound"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    description='Suspense like tag for reactpy library or lilliepy framework',
    keywords=[
        "lilliepy", "lilliepy-rebound", "reactpy"
    ],
    author='Sarthak Ghoshal',
    author_email='sarthak22.ghoshal@gmail.com',
    license='MIT',
    python_requires='>=3.6',
)