from setuptools import setup, find_packages

setup(
    name="PyAiTrainer",
    version="0.1.1",
    author="I'm_caca",
    author_email="",
    description="Minimal transformer-based character-level trainer",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/timurko7674/PyTrainer",  # Your repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "torch>=1.0",
        # Add any other dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
