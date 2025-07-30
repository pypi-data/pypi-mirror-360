from setuptools import setup, find_packages

setup(
    name="gazooresearchutils",
    version="1.10.11",
    description="Analysis of GazooResearch Data",
    package_dir={"":"app"},
    packages=find_packages(where="app"),
    url="https://gazooresearch.com/",
    author='Andrew Lim MD, Megan Lim MD, Christopher Lim MD, Robert Lim MD',
    install_requires=["lifelines >= 0.28.0", "pandas>=2.1.0", "pydantic>=2.11.7"],
    python_requires=">=3.10"
)
