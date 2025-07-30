from setuptools import setup, find_packages

setup(
    name="dynaroute-client",
    version="1.0.2",
    author="Vizuara",
    author_email="teamvizuara@gmail.com",
    description="A client for interacting with the DynaRoute API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Vizuara-LLM/dynaroute-py",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
