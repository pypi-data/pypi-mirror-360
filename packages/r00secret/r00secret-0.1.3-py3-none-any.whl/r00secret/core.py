from dataclasses import dataclass
from pathlib import Path

from box import Box
from r00logger import log

from .helpers.constants import SECRET_FILE


@dataclass
class ArangoDB:
    user: str
    paswd: str
    host: str
    port: int


@dataclass
class RabbitMQ:
    user: str
    paswd: str
    host: str
    port: int


@dataclass
class CoinMarketCap:
    apikeys: list


@dataclass
class Binance:
    api_key: str
    api_secret: str


@dataclass
class Telegram:
    chat_crypto: str
    chat_notify: str
    chat_warn: str


@dataclass
class DockerHub:
    user: str
    paswd: str


@dataclass
class Fileserver:
    host: str


@dataclass
class Sercet:
    arangodb: ArangoDB
    rabbitmq: RabbitMQ
    coinmarketcap: CoinMarketCap
    binance: Binance
    telegram: Telegram
    dockerhub: DockerHub
    fileserver: Fileserver


def get_secret_data() -> Sercet | None:
    filepath = Path(SECRET_FILE)
    if filepath.exists():
        return Box().from_yaml(filename=filepath)
    log.warning('Secret file not found')


secret = get_secret_data()
