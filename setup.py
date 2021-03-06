from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="joey",
    version="0.4.0",
    description="Async web framework on top of fastapi and orm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pinecrew/joey",
    author="pinecrew",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="joey web framework orm fastapi",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    python_requires=">=3.8, <4",
    install_requires=[
        "alembic==1.4.2",
        "fastapi==0.61.0",
        "orm==0.1.5",
        "pytz==2020.1",
        "mako==1.1.3",
        "click==7.1.2",
        "pyyaml==5.3.1",
    ],
    extras_require={"dev": ["black==19.10b0", "pylint", "pytest", "aiosqlite"], "sessions": ["pyjwt==1.7.1", "cryptography==3.0"]},
    entry_points={'console_scripts': ['joey=joey.cli:main'],},
    dependency_links=[],
    include_package_data=True,
    project_urls={},
)
