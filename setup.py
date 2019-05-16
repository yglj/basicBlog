
from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.1',
    packages=find_packages(),
    include_packages_date=True,   # 不是exclude
    zip_safe=False,
    install_requires=[
        'flask',
    ]
)
