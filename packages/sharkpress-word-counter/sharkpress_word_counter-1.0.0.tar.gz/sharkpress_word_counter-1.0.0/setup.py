from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sharkpress-word-counter",
    version="1.0.0",
    author="Wiktor Jachec",
    author_email="hello@sharkpress.agency",
    description="A tool to count words in the main content of web pages, ignoring cookie banners and other non-content elements.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sharkpress/url-word-counter",
    project_urls={
        'Bug Reports': 'https://github.com/sharkpress/url-word-counter/issues',
        'Source': 'https://github.com/sharkpress/url-word-counter',
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=4.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "url-word-counter=url_word_counter.core:main",
        ],
    },
)
