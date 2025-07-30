
from setuptools import setup, find_packages

setup(
    name="pyeasyal",
    version="0.1.0",
    packages=find_packages(),
    description="Make Python easier and friendlier!",
    author="Alhawari Code",
    author_email="alhawari.officail@gmail.com",
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
