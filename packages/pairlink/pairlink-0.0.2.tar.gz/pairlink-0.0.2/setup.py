from setuptools import setup, find_packages

setup(
    name='pairlink',
    version='0.0.2',
    description='A package for statistical analysis and testing of relationships between 2 time series.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Anthony Gocmen',
    author_email='anthony.gocmen@gmail.com',
    url='https://www.developexx.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.11',
    install_requires=[
        'pandas',
        'numpy',
        'statsmodels',
        'scipy'
    ],
    license='MIT'
)