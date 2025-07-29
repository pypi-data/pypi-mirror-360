from setuptools import setup, find_packages

setup(
    name="MeowMod",
    version="2.7.2.9",
    author="小孫孫",
    author_email="sun1000526@gmail.com",
    description="Battle Cats Save File Editor - 修改器套件",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "MeowMod": ["files/*", "files/locale/*"],
    },
    install_requires=[
        "colored==1.4.4",
    ],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "meowmod = MeowMod.__main__:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
