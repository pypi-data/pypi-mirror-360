# myproject/setup.py

from setuptools import setup, find_packages

setup(
    name="vecx",
    version="0.33.1b2",
    packages=find_packages(),
    package_data={
        '': ['libvx/*'],  # Include all files in the libvx directory
    },
    install_requires=[
        # List your dependencies here
        "requests>=2.28.0",
        "numpy>=2.2.4",
        "msgpack>=1.1.0",
        "cffi>=1.17.1",
    ],
    author="LaunchX Labs",
    author_email="support@vectorxdb.ai",
    description="Encrypted Vector Database for Secure and Fast ANN Searches",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://vectorxdb.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
