from setuptools import setup, find_packages

setup(
    name='my_test_calculator_pkg',
    version = '0.0.1',
    author = 'anil',
    author_email='anilsai029@gmail.com',
    description= 'A basic calculator package',
    long_description=open('README.md','r',encoding= 'utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires = '>=3.6',
    entry_points = {
        'console_scripts':[
            "calculator_pkg = calculator_package.math_operations_module",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent"
    ],
)