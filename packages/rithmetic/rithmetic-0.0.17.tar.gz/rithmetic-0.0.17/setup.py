from setuptools import setup, find_packages

with open("README.md", "r", encoding='UTF-8') as f:
    long_description = f.read()

setup(
    name= 'rithmetic',
    version= '0.0.17',
    packages= find_packages(),
    install_requires= [],
    description= "Simple arithmetic lib for students",
    long_description=long_description,
    long_description_content_type= "text/markdown",
    url= "https://github.com/Prashant-Aswal/rithmetic",
    author= "PrashantAswal",
    author_email= "prashant.aswal89@gmail.com",
    license= "MIT",
    license_files= ["LICENSE.md",],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "rith = rithmetic:welcome",
            "rith-version = rithmetic:ver",
        ],
    },
)