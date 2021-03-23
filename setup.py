from setuptools import find_packages, setup  # type: ignore


REQUIREMENTS = [
    "aiohttp",
    "SQLAlchemy",
    "asyncpgsa",
    "pydantic",
    "yarl",
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
