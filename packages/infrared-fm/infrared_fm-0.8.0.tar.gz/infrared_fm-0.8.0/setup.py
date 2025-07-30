from setuptools import setup, find_packages
# we go dumm
setup(
    name="infrared-fm",
    version="0.8.0",
    description="Last.FM wrapper by Infrared LLC.",
    author="infrared",
    author_email="faneorg.official@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/infraredhuh/infrared-fm",
    package_data={"infrared.fm": ["py.typed"]},
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
