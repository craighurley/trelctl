from . import client


def get_labels(board_id: str) -> list[dict]:
    """Fetch all labels for a board."""
    return client.get(f"/boards/{board_id}/labels")
