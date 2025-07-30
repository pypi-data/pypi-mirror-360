import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="subreader",
    version="0.0.1",
    author="aipiecool",
    author_email="aipiecool@example.com",
    description="read srt, ass files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xinglufan/subreader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'apnode>=0.0.1',
        'ass>=0.5.4',
        'chardet>=5.2.0',
    ],
)

# python setup.py sdist bdist_wheel
#