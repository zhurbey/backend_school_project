from setuptools import find_packages, setup  # type: ignore


REQUIREMENTS = [
    "aiohttp==3.7.4",
    "SQLAlchemy==1.3.23",
    "asyncpgsa==0.27.1",
    "pydantic==1.8.1",
    "yarl==1.6.3",
    "pytz==2021.1"
]

DEV_REQUIREMENTS = [
    "pytest",
    "mypy",
    "black",
    "isort",
]


setup(
    name="backend_school",
    version="1.0",
    description="yandex backend school project test task",
    author="Zhurbey Sergey",
    author_email="zhurbey.sergey@yandex.ru",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": DEV_REQUIREMENTS,
    },
    entry_points={
        "console_scripts": [
            "sweets_store.api = sweets_store.api.__main__:run_server",
        ]
    },
)
