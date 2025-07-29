from setuptools import setup, find_packages

setup(
    name="Ntldz",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "DrissionPage>=4.1.0.18",
        "pydub>=0.25.1",
        "SpeechRecognition>=3.14.3",
    ],
)