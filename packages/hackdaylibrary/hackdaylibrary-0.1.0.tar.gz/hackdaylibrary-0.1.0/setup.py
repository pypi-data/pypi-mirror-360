from setuptools import setup, find_packages

setup(
    name="hackdaylibrary",
    version="0.1.0",
    description="Powerful ethical hacking Python library",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your_username/hackday",
    packages=find_packages(),
    install_requires=[
        "PyAudio~=0.2.14",
        "requests~=2.32.4",
        "opencv-python~=4.11.0.86",
        "psutil~=7.0.0",
        "dnspython~=2.7.0",
        "PyPDF2~=3.0.1",
        "jwt~=1.4.0",
        "beautifulsoup4~=4.13.4",
        "cryptography~=45.0.5",
    ],
    python_requires='>=3.7',
)
