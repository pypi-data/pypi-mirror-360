from setuptools import setup, find_packages

setup(
    name="dj-vditor-widget",
    version="0.3.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django>=4.0"],
    extras_require={
        "oss": ["oss2>=2.15.0"],
        "tos": ["tos-python-sdk"],
        "all": ["oss2>=2.15.0", "tos-python-sdk"],
    },
    description="Django Textarea Widget Integrated Vditor with Customizable Configuration",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/ren000thomas/dj-vditor-widget",
    author="Ren Thomas",
    author_email="ren000thomas@gmail.com",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
