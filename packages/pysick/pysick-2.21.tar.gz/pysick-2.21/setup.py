from setuptools import setup

setup(
    name="pysick",
    version="2.21",
    license="MIT",
    packages= ['pysick'],
    package_data={'pysick':['assets/*.ico','assets/*.png']},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pysick = pysick.shell:main",
        ],
    },
    author="CowZik",
    author_email="cowzik@email.com",
    description='An Bypass for learning Graphics Development',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/COWZIIK/pysick",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
