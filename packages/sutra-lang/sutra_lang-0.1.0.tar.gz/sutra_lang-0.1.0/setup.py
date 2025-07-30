from setuptools import setup, find_packages

setup(
    name="sutra-lang",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sutra = sutra.sutra_lang:main',
        ],
    },
    author="Viral Mehta",
    author_email="your@email.com",
    description="Sutra: A Hindi programming language built on top of Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vickydevlab/sutra-lang",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
