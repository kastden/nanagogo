import setuptools

setuptools.setup(
    name="nanagogo",  # Replace with your own username
    author="kastden",
    description="Python library for the 7gogo.jp private API",
    url="https://github.com/kastden/nanagogo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    'requests>=2.21.0',
])
