from setuptools import setup, find_packages

setup(
    name="tushell",
    version = "0.2.20",
    description="The Data Diver's best Intelligent and Narrative Command-Line Tooling you will have ever had",
    author="JGWill",
    author_email="tushellframe@jgwill.com",
    url="https://github.com/jgwill/tushell",
    packages=find_packages(
        include=["tushell", "tushell.*", "test-*.py"], exclude=["test*log", "*test*csv", "*test*png"]
    ),
    #include_package_data=True,
    install_requires=[
        "click",
        "requests",
        "python-dotenv",
        "PyYAML",
    ]
)
