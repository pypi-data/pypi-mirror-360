from setuptools import setup, find_packages

setup(
    name="samhiqmailer",
    version="2.6",
    author="Md Sameer Iqbal (Samhiq)",
    author_email="contact.samhiq@gmail.com",
    description="Professional Email Sender App with Excel, HTML, and Notifications",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/samhiq/SamhiqMailer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openpyxl",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
