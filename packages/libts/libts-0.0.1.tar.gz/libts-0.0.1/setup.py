import setuptools

with open("README.md", "r", encoding = "utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name = "libts",
    version = "0.0.1",
    author = "Brassinolide",
    author_email = "contact@crackme.net",
    description = "一个用于验证 RFC3161 时间戳签名的库",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Brassinolide/libts-py",
    packages = setuptools.find_packages(),
    package_data = {
        "libts": ["*.dll", "*.so"],
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
)
