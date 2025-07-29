from setuptools import setup, find_packages

setup(
    name="django_watchlog_apm",
    version="0.1.4",
    packages=find_packages(),
    description="Watchlog APM integration for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohammadreza",
    license="MIT",
    python_requires=">=3.7",
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    project_urls={
        "Watchlog": "https://watchlog.io",
        "Source": "https://github.com/watchlogserver/django_watchlog_apm.git"
    }
)
