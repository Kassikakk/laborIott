from setuptools import setup, find_namespace_packages

setup(
    name='laborIott',
    version='1.0.0',    
    description='labori IoT',
    packages=['laborIott'] + find_namespace_packages(include=['laborIott.*']),
                      ) 
