from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyvoicecraft",
    version="1.0.0",
    author="Kodukulla.Phani Kumar",
    author_email="phanikumark715@gmail.com",
    description="Advanced voice processing package with comprehensive TTS and speech recognition capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodukulla-phani-kumar/pyvoicecraft",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.8.1",
        "PyAudio>=0.2.11",
        "numpy>=1.19.0",
        "scipy>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyvoicecraft=pyvoicecraft.cli:main",
        ],
    },
    keywords="voice, speech, tts, text-to-speech, speech-recognition, audio, voice-processing",
    project_urls={
        "Bug Reports": "https://github.com/kodukulla-phani-kumar/pyvoicecraft/issues",
        "Source": "https://github.com/kodukulla-phani-kumar/pyvoicecraft",
        "Documentation": "https://github.com/kodukulla-phani-kumar/pyvoicecraft/wiki",
    },
)