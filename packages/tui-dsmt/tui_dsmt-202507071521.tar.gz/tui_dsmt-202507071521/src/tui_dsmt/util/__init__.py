from uuid import uuid4


def unique_name() -> str:
    return str(uuid4()).replace('-', '')
