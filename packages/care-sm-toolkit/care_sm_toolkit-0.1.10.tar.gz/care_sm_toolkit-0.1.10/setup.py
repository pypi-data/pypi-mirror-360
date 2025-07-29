from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="care_sm_toolkit",
    version="0.1.10",
    packages=find_packages(exclude=["toolkit.API", "toolkit.API.*"]),
    author="Pablo Alarcón Moreno",
    author_email="pabloalarconmoreno@gmail.com",
    url="https://github.com/CARE-SM/CARE-SM-Toolkit",
    description="A toolkit for CARE-SM data transformation.",
    long_description="See README.md",
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["FAIR-in-a-box", "Fiab", "CARE-SM", "Toolkit"],
    project_urls={
        "Source": "https://github.com/CARE-SM/CARE-SM-Toolkit",
        "Bug Tracker": "https://github.com/CARE-SM/CARE-SM-Toolkit/issues",
    },
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
        ],
    },
    include_package_data=True,

)