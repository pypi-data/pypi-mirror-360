from setuptools import setup, find_packages

setup(
    name='chayan',
    version='2.0.1',
    description='Library to fetch nifty midcap, largecap and smallcap stocks.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Amit Kumar Sharma',
    author_email='amit.official@gmail.com',
    url='https://github.com/sharmaak/chayan',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.8',
)
