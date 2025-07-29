from setuptools import setup, find_packages

setup(
    name="ultra-crdex",
    version="6.1",
    packages=find_packages(),
    package_data={
        'ULTRA': [
            'lib/python3.9/site-packages/ULTRA.so',
            'lib/python3.11/site-packages/ULTRA.so',
            'lib/python3.12/site-packages/ULTRA.so'
        ]
    },
    author="CRDEX",
    author_email="aymanambaby507@gmail.com",
    description='new compiler to enc files python',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
)