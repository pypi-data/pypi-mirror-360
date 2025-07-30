import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bowcar", ## 소문자 영단어
    version="0.0.2", ##
    author="ITPLE", ## ex) Sunkyeong Lee
    author_email="itple@itpleinfo.com", ##
    description="A package for controlling a bowcar // 바우카를 사용하기 위한 모듈", ##
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/itple-books/BowCar", ##
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)