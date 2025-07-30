from setuptools import setup, find_packages

setup(
    name='wlc-sdk-financeiro',
    version='1.0.0',
    description='SDK for Finance Module',
    author='WLC Soluções',
    author_email='analiciasouza.11@gmail.com',
    url='https://github.com/wlc-solucoes/wlc-sdk-financeiro.git',
    packages=find_packages(),
    install_requires = ["django", "djangorestframework"],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django' , 
        'Intended Audience :: Developers', 
        'Programming Language :: Python'
     ],
    
)