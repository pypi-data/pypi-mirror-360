from setuptools import setup, find_packages

setup(
    name="meowmod",
    version="2.7.2.11",
    author="小孫孫",
    author_email="sun1000526@gmail.com",
    description="Battle Cats Save File Editor - 修改器套件",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "meowmod": ["files/*", "files/locale/*"],
    },
    install_requires=[
        "colored==1.4.4",
        "pyyaml==6.0.2"
    ],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "meowmod = meowmod.__main__:main",
        ],
    },
)
