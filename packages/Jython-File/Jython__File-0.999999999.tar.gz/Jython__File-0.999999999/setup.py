from setuptools import setup, find_packages

setup(
    name='Jython__File',
    version='0.999999999',
    packages=find_packages(),
    author='D',
    author_email='nasr2python@gmail.com',
    description='What',
    include_package_data=True,
    package_data={
        'java_code': ['*.so'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)