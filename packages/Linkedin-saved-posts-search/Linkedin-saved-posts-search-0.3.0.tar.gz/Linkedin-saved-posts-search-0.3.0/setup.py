from setuptools import setup, find_packages

setup(
    name="Linkedin-saved-posts-search",  
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver-manager",
        "beautifulsoup4",
        "rapidfuzz"
    ],
    entry_points={
        "console_scripts": [
            "Lsps=Linkedin_saved_posts_search.main:main",
        ],
    },
    author="Milad Tajvidi",
    author_email="milad.tajvidi@gmail.com",
    description="A CLI tool to scrape and search your LinkedIn saved posts.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/miladtajvidi/Linkedin_Saved_Posts_Search",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)
