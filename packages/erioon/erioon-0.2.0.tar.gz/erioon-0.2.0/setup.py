from setuptools import setup, find_packages

setup(
    name='erioon',
    version='0.2.0',
    author='Zyber Pireci',
    author_email='zyber.pireci@erioon.com',
    description='Erioon Python SDK for seamless interaction with Erioon data services',
    long_description=(
        "The Erioon SDK for Python provides a robust interface to interact "
        "with Erioon resources such as collections, databases, and clusters. "
        "It supports CRUD operations, querying, and connection management "
        "with ease, enabling developers to integrate Erioon data services "
        "into their applications efficiently."
    ),
    long_description_content_type='text/plain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    packages=['erioon'],
    install_requires=[
        'requests>=2.25.1',
        'pyodbc',
        'azure-storage-blob',
        'msgpack',
    ],
    python_requires='>=3.6',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)
