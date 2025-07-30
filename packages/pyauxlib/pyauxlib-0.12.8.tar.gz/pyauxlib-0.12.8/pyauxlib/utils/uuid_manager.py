"""Create unique UUID objects (universally unique identifiers)."""

import uuid


def is_uuid_unique(uuid_val: uuid.UUID, existing_uuids: list[uuid.UUID]) -> bool:
    """
    Check if a UUID is unique.

    Parameters
    ----------
    uuid_val : uuid.UUID
        The uuid to check.
    existing_uuids : list of uuid.UUID
        The list of existing UUIDs.

    Returns
    -------
    bool
        True if the id is unique, False otherwise.
    """
    return uuid_val not in existing_uuids


def generate_unique_uuid(existing_uuids: list[uuid.UUID] | None = None) -> uuid.UUID:
    """
    Generate a unique random UUID.

    Parameters
    ----------
    existing_uuids : list of uuid.UUID, optional
        The list of existing UUIDs. If not provided, a random UUID is generated.

    Returns
    -------
    uuid.UUID
        A new unique id.
    """
    while True:
        new_id = uuid.uuid4()
        if existing_uuids is None or is_uuid_unique(new_id, existing_uuids):
            return new_id
