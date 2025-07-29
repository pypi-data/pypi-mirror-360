from setuptools import setup, find_packages

setup(
    name="junklang",
    version="0.1.0",
    description="A junk programming language",
    author="Abhay Gupta",
    author_email="abhaygupta.hsj@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'junk=__main__:run_cli',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)