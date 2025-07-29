from setuptools import setup, find_packages

setup(
    name="Usman_Ghani",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    author="Usman Ghani",
    description="Python installable biography of Usman Ghani",
    long_description="Installable resume and profile of Usman Ghani.",
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
