from setuptools import setup, find_packages

setup(
    name="rawa_bots",
    version="0.2.0",
    description="A Python library to easily build Gemini-powered chatbots and generate images.",
    author="Your Name or Organization",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],  # To be updated with Gemini SDK
    python_requires=">=3.8",
) 