from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.integrations.keitaro.client import KeitaroClient


def get_keitaro_client(
    settings: Settings = Depends(get_settings),
) -> Generator[KeitaroClient, None, None]:
    client = KeitaroClient(settings)
    try:
        yield client
    finally:
        client.close()