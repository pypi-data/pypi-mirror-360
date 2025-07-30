import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HalaGPT",  # اسم المكتبة على PyPI (تأكد أنه غير مستخدم)
    version="1.20.0",
    author="WOLF",
    description="A simple library for many AI APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),  # بدون where
    python_requires=">=3.6",
    install_requires=[
        "bs4",
        "requests",
        "user_agent",
        "mnemonic",
    ],
)