from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="growwmcp",
    version="0.1.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "growwmcp": ["../prompt.yaml"],
    },
    entry_points={
        "console_scripts": [
            "growwmcp=growwmcp.main:main",  # Optional: direct command
        ],
    },
    author="Sayan Dey",
    author_email="sayand@groww.in",
    description="Groww MCP package",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/Groww/ml-growwmcp",
    python_requires=">=3.10",
)
