import uuid


def gen_id() -> str:
    """Creates unique id.

    Returns:
        Id created.
    """
    return uuid.uuid4().hex
