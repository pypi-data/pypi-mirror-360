from setuptools import setup, find_packages

setup(
    name="magentic-olly",
    version="0.1.0",
    description="Magentic AI. opentelemtry instrumentation package",
    packages=find_packages(include=["magentic_olly", "magentic_olly.*"]),
    install_requires=[],
    python_requires=">=3.9, <4.0",
    include_package_data=True,
)
