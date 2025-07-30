from setuptools import setup, find_packages

setup(
    name="madnansultan",
    version="0.1.0",
    description="Portfolio of Muhammad Adnan Sultan as a Python package (CLI and Web)",
    author="Muhammad Adnan Sultan",
    author_email="info.adnansultan@gmail.com",
    url="https://github.com/madnansultandotme",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0.0",
        "reportlab>=3.6.0"
    ],
    entry_points={
        "console_scripts": [
            "madnansultan=madnansultan.cli:main",
            "madnansultan-web=madnansultan.web:app.run"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 