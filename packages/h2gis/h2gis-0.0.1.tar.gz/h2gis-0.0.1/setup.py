from setuptools import find_packages, setup

setup(
    name='h2gis',
    version='0.0.1',
    description='A Python library to use an H2GIS database through a native GraalVM bridge.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Lemap',
    author_email='you@example.com',  # Optional, but recommended
    url='https://github.com/yourusername/h2gis',  # Replace with actual URL
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "h2gis": ["lib/*.so", "lib/*.dll", "lib/*.dylib"],
        "h2gis.docs": ["*.md"],  # add this if docs is inside the h2gis package
    },
    license="LGPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
)
