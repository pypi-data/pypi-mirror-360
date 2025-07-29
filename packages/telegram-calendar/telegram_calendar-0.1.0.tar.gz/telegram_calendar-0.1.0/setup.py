from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="telegram-calendar",
    version="0.1.0",
    author="S-i1-V",
    author_email="vanosaprikin@gmail.com",
    description="Telegram calendar builder library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SI1V/tg_calendar.git",
    packages=find_packages(exclude=["example", "venv", "tests*"]),
    python_requires='>=3.10',
    install_requires=[
        "aiofiles==24.1.0",
        "aiogram==3.20.0.post0",
        "aiohappyeyeballs==2.6.1",
        "aiohttp==3.11.18",
        "aiosignal==1.4.0",
        "annotated-types==0.7.0",
        "async-timeout==5.0.1",
        "attrs==25.3.0",
        "certifi==2025.6.15",
        "frozenlist==1.7.0",
        "idna==3.10",
        "magic-filter==1.0.12",
        "multidict==6.6.3",
        "propcache==0.3.2",
        "pydantic==2.11.7",
        "pydantic_core==2.33.2",
        "python-dotenv==1.1.1",
        "typing-inspection==0.4.1",
        "typing_extensions==4.14.1",
        "yarl==1.20.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
)
