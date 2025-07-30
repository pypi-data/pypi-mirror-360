from setuptools import setup, find_packages

setup(
    name="bsdk",
    version="0.0.1",
    description="Easy to copy package",
    author="Unknown",
    author_email="rugvedapraj1@gmail.com",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'bsdk=bsdk.core:start',
        ],
    },
    python_requires=">=3.6",
    include_package_data=True,
)
