from setuptools import setup, find_packages

setup(
    name='myshop',
    version='0.0.1-alpha',
    description="un programme qui s'occupe de la gestion de stock dans une boutique",
    author="Jephte Mangenda",
    author_email='tech5industrie@gmail.com',
    packages=find_packages(),
    package_data={
        'myshop':['logo.ico']
    },
    include_package_data=True,
    requires=[
        'sqlalchemy',
        'configparser',
        'flask',
        'matplotlib',
        'win32print',
        'reportlab',
        'gunicorn'
    ],
    entry_points={
        "console_scripts": [
            "myshop = myshop.console:main",
        ],
    },
)