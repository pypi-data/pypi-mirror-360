from setuptools import setup, find_packages

setup(
    name='mememo',
    version='1.1',
    description='Lightweight package to find the mean, median, and mode.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='dUhEnC-39',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.5',
)
