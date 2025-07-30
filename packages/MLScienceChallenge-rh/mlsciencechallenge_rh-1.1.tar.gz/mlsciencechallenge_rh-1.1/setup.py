import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "MLScienceChallenge_rh",
    version = "1.1",
    author = "Raymond Hawkins",
    author_email = "raymond.hawkins@mail.utoronto.ca",
    description = "ML Science Coding Challenge for CZI Biohub application.",
    url = "https://github.com/rayhawkins/MLScienceChallenge",
    project_urls = {
        "Bug Tracker": "https://github.com/rayhawkins/MLScienceChallenge/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3.10"
)