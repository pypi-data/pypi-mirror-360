from setuptools import setup
from pathlib import Path

long_description = (Path(__file__).parent / 'README.md').read_text(encoding='utf-8')

setup(
    name='lilliepy-tags',
    version='0.0.2',
    install_requires=[],
    packages=["lilliepy_tags"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    description='jsx like tag system for reactpy library or lilliepy framework',
    keywords=[
        "lilliepy", "lilliepy-tags", "reactpy"
    ],
    author='Sarthak Ghoshal',
    author_email='sarthak22.ghoshal@gmail.com',
    license='MIT',
    python_requires='>=3.6',
)