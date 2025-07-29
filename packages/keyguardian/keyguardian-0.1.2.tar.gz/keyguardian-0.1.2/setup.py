from setuptools import setup, find_packages

setup(
    name='keyguardian',
    version='0.1.2',
    author="Krishna Agarwal",
    author_email="krishnacool781@gmail.com",
    description="A Python package for securely generating and managing encryption keys.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/krishnaagarwal781/mask_keys_server",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'keyguardian-setup=keyguardian.cli:setup',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
