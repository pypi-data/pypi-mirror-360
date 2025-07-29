from setuptools import setup, find_packages

setup(
    name='shahanshahi_calendar',
    version='0.1.2',
    description='The Imperial (Shahanshahi) calendar system for Python',
    author='Morteza Shoeibi',
    author_email='mortezashoeibi77@gmail.com',
    packages=find_packages(),
    install_requires=['jdatetime'],
    license="Python Software Foundation License",
    python_requires='>=3.7',
)
