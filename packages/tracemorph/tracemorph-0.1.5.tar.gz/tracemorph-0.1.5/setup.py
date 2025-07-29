from setuptools import setup, find_packages

setup(
    name="tracemorph",
    version="0.1.5",
    author="Hadi",
    author_email="lahadiyani@gmail.com",
    description="Function execution tracing, visualization, and narrative builder for Python apps.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lahadiyani/tracemorph",  # Ganti sesuai repo GitHub kamu
    packages=find_packages(exclude=["tests*", "examples*"]),
    include_package_data=True,
    install_requires=[
        "requests",
        "flask",
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
    ],
    license="Custom NonCommercial License",
    python_requires=">=3.7",
)
