from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jamanger",
    version="1.0.0",
    author="JaManager Team",
    author_email="team@jamanger.com",
    description="A modern jam session management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jamanger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jamanger=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "jamanger": ["static/*", "static/**/*"],
    },
)
