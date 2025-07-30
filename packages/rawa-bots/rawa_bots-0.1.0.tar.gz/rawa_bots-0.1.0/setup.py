from setuptools import setup, find_packages

setup(
    name="rawa_bots",
    version="0.1.0",
    description="A Python library to easily build Gemini-powered chatbots.",
    author="Your Name or Organization",
    packages=find_packages(),
    install_requires=[
        "google-genai>=0.1.0"
    ],  # To be updated with Gemini SDK
    python_requires=">=3.8",
) 