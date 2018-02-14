from setuptools import find_packages, setup


setup(
    name='pytasks',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'task=tasks:cli'
        ]
    }
)
