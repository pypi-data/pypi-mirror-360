import os
from typing import List

from arango import ArangoClient
from arango.client import StandardDatabase
from arango.exceptions import CollectionCreateError
from r00logger import log
from r00secret import secret



def _get_credentials():
    credentials = {
        "host": os.getenv("ARANGO_HOST"),
        "user": os.getenv("ARANGO_USER"),
        "paswd": os.getenv("ARANGO_PASWD"),
    }

    for key, value in credentials.items():
        if key == 'host' and not value:
            credentials['host'] = secret.arangodb.host

        elif key == 'user' and not value:
            credentials['user'] = secret.arangodb.user

        elif key == 'paswd' and not value:
            credentials['paswd'] = secret.arangodb.paswd

    return credentials.values()


def _initialize_collections(db, collections: List[str]) -> StandardDatabase:
    """
    Инициализирует коллекции в базе данных.
    :param collections: Список названий коллекций для создания.
    """
    for collection_name in collections:
        try:
            if not db.has_collection(collection_name):
                log.info(f"Коллекция '{collection_name}' не найдена, создаем...")
                db.create_collection(collection_name)
        except CollectionCreateError as e:
            log.error(f"Ошибка создания коллекции '{collection_name}': {e}")
            exit(1)
    return db


def connect_arango(dbname: str, initialize_collections: List[str] = None) -> StandardDatabase:
    """
    Подключается к базе данных ArangoDB и создает базу данных, если она не существует.
    :param dbname: Имя базы данных.
    :param initialize_collections: Список названий коллекций для создания.
    :return:
    """
    host, user, paswd = _get_credentials()
    try:
        client = ArangoClient(hosts='http://' + host + ":8529")
        db_system = client.db('_system', username=user, password=paswd)
        db_system.status()
    except Exception as e:
        log.error(f"Ошибка подключения к ArangoDB: {e}")
        exit(1)

    if not db_system.has_database(dbname):
        db_system.create_database(dbname)

    db_target = client.db(dbname, username=user, password=paswd)

    if initialize_collections:
        _initialize_collections(db_target, initialize_collections)

    return db_target
