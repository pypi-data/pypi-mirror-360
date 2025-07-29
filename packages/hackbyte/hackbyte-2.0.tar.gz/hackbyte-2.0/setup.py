from setuptools import setup, find_packages
from hackbyte.version import __version__

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='hackbyte',
    version=__version__,
    author='Dx4Grey',
    author_email='dxablack@gmail.com',
    description="HackByte is a powerful CLI memory scanner and modifier for rooted Linux and Android.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/DX4GREY/hackbyte',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'hackbyte = hackbyte.__main__:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    keywords="memory scanner cli android root linux hacking freeze reverse-engineering",
    python_requires='>=3.6',
)