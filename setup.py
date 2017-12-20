from setuptools import setup, find_packages


setup(
    name="dsatest",
    version="0.0.1",
    author="Damien Riegel",
    author_email="damien.riegel@savoirfairelinux.com",
    description="A Linux network testing framework for hardware switching devices",
    packages=find_packages(),
    package_data={
        # Include config files:
        '': ['conf/*/*.cfg',],
    },
    entry_points={
        'console_scripts': ['dsatest = dsatest.bench.runner:main',]
    },
)
