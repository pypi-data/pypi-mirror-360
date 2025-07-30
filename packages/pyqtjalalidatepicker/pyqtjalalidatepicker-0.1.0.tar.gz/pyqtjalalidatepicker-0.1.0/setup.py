from setuptools import setup, find_packages

setup(
    name="pyqtjalalidatepicker",
    version="0.1.0",
    author="Sadegh Naghibzadeh",
    author_email="sadng11@gmail.com",
    description="A Jalali date picker widget for PyQt5",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sadng11/pyqt-jalali-date-picker",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "jdatetime>=4.2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)