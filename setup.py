from setuptools import setup, find_packages

setup(
    name='myshop',
    version='0.0.1a0',
    description="un programme qui s'occupe de la gestion de stock dans une boutique",
    author="Jephte Mangenda",
    author_email='tech5industrie@gmail.com',
    packages=find_packages(),
    package_data={
         'myshop':['myshop_server/.env']
    },
    include_package_data=True,
    requires=[
        'sqlalchemy',
        'configparser',
        'flask',
        'matplotlib',
        'win32print',
        'reportlab',
        'waitress'
    ],
    entry_points={
        "console_scripts": [
            "myshop_server = myshop_server.console:main",
            "myshop_client = myshop_client.console:main",
        ],
    },
)
