from setuptools import setup
setup(
    name="bump-setup",
    version='1.2.0',
    description="A tool to bump the version in setup.py in python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="@readwithai",
    author_email="talwrii@googlemail.com.com",
    url="https://github.com/talwrii/bump-setup",
    packages=["bump_setup"],
    install_requires=["toml", "tree-sitter", "tree-sitter-python"],
    entry_points={
        "console_scripts": [
            "bump-setup=bump_setup.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
