from setuptools import setup, find_packages

setup(
    name='procmodeling',
    version='1.0.0',
    author='tenoriolms',
    description='',
    long_description='',#open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tenoriolms/procmodeling_lib',
    packages=find_packages(),
    install_requires=[
        'numpy>=2.2.4', 
        'pandas>=2.2.3', 
        'matplotlib>=3.10.1',
        'scipy>=1.15.2',
        'sympy>=1.13.3',
        ],  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True, #For include text .txt files
)