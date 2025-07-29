from setuptools import setup, find_packages

setup(
    name="deep-consultation",
    version="0.1.1",
    packages=find_packages(),
    author="Fernando Pujaico Rivera",
    author_email="fernando.pujaico.rivera@gmail.com",
    description="A library for queries with GPTs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/trucomanx/DeepConsultation",
    license='GPLv3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
       "OpenAI"
    ],
)

