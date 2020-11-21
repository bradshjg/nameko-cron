import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nameko-cron",
    version="0.1.0",
    author="bradshjg",
    author_email="james.g.bradshaw@gmail.com",
    description="Nameko cron extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bradshjg/nameko-cron",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.6',
    install_requires=[
        'croniter',
        'nameko',
        'pytz'
    ]
)
