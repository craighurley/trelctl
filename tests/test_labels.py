import httpx
import pytest
import respx

from trelctl.trello.labels import get_labels

BASE = "https://api.trello.com/1"
BOARD_ID = "board123"


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRELLO_API_KEY", "test-key")
    monkeypatch.setenv("TRELLO_TOKEN", "test-token")


@respx.mock
def test_get_labels_returns_list() -> None:
    labels_data = [
        {"id": "lbl1", "name": "Bug"},
        {"id": "lbl2", "name": "Feature"},
    ]
    respx.get(f"{BASE}/boards/{BOARD_ID}/labels").mock(
        return_value=httpx.Response(200, json=labels_data)
    )
    result = get_labels(BOARD_ID)
    assert result == labels_data


@respx.mock
def test_get_labels_empty_board() -> None:
    respx.get(f"{BASE}/boards/{BOARD_ID}/labels").mock(return_value=httpx.Response(200, json=[]))
    result = get_labels(BOARD_ID)
    assert result == []
