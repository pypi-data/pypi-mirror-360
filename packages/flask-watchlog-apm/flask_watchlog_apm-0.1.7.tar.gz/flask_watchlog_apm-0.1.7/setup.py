from setuptools import setup, find_packages

setup(
    name="flask_watchlog_apm",
    version="0.1.7",
    description="Lightweight APM for Flask that sends metrics to Watchlog Agent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza",
    author_email="mohammadnajm75@gmail.com",
    url="https://github.com/watchlogserver/flask_watchlog_apm",
    packages=find_packages(),
    install_requires=["Flask", "psutil", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
