import httpx
import pytest
import respx

from trelctl.trello.cards import (
    create_card,
    create_check_item,
    create_checklist,
    get_board_cards,
    get_card_checklists,
    get_list_cards,
)

BASE = "https://api.trello.com/1"


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRELLO_API_KEY", "test-key")
    monkeypatch.setenv("TRELLO_TOKEN", "test-token")


# --- create_card ---


@respx.mock
def test_create_card_minimal() -> None:
    respx.post(f"{BASE}/cards").mock(
        return_value=httpx.Response(200, json={"id": "card1", "name": "Fix bug"})
    )
    result = create_card(list_id="list1", name="Fix bug")
    assert result["id"] == "card1"
    assert result["name"] == "Fix bug"


@respx.mock
def test_create_card_with_all_fields() -> None:
    route = respx.post(f"{BASE}/cards").mock(
        return_value=httpx.Response(200, json={"id": "card1", "name": "Fix bug"})
    )
    create_card(
        list_id="list1",
        name="Fix bug",
        desc="Steps to reproduce",
        label_ids=["lbl1", "lbl2"],
        due="2026-04-15T00:00:00.000Z",
        member_ids=["mem1", "mem2"],
    )
    url = str(route.calls[0].request.url)
    assert "desc=Steps+to+reproduce" in url or "desc=" in url
    assert "lbl1" in url
    assert "lbl2" in url
    assert "2026-04-15" in url
    assert "mem1" in url


@respx.mock
def test_create_card_empty_optionals_not_sent() -> None:
    route = respx.post(f"{BASE}/cards").mock(
        return_value=httpx.Response(200, json={"id": "card1", "name": "Fix bug"})
    )
    create_card(list_id="list1", name="Fix bug")
    url = str(route.calls[0].request.url)
    assert "desc" not in url
    assert "idLabels" not in url
    assert "due" not in url
    assert "idMembers" not in url


# --- create_checklist ---


@respx.mock
def test_create_checklist() -> None:
    route = respx.post(f"{BASE}/cards/card1/checklists").mock(
        return_value=httpx.Response(200, json={"id": "cl1"})
    )
    result = create_checklist("card1")
    assert result["id"] == "cl1"
    assert "Checklist" in str(route.calls[0].request.url)


# --- create_check_item ---


@respx.mock
def test_create_check_item() -> None:
    route = respx.post(f"{BASE}/checklists/cl1/checkItems").mock(
        return_value=httpx.Response(200, json={"id": "ci1", "name": "Write tests"})
    )
    result = create_check_item("cl1", "Write tests")
    assert result["id"] == "ci1"
    assert "Write+tests" in str(route.calls[0].request.url) or "Write" in str(
        route.calls[0].request.url
    )


# --- get_board_cards ---


@respx.mock
def test_get_board_cards() -> None:
    cards = [{"id": "c1", "name": "Card 1"}, {"id": "c2", "name": "Card 2"}]
    respx.get(f"{BASE}/boards/board1/cards").mock(return_value=httpx.Response(200, json=cards))
    result = get_board_cards("board1")
    assert result == cards


# --- get_list_cards ---


@respx.mock
def test_get_list_cards() -> None:
    cards = [{"id": "c1", "name": "Card 1"}]
    respx.get(f"{BASE}/lists/list1/cards").mock(return_value=httpx.Response(200, json=cards))
    result = get_list_cards("list1")
    assert result == cards


# --- get_card_checklists ---


@respx.mock
def test_get_card_checklists() -> None:
    checklists = [{"id": "cl1", "checkItems": [{"name": "Step 1"}]}]
    respx.get(f"{BASE}/cards/card1/checklists").mock(
        return_value=httpx.Response(200, json=checklists)
    )
    result = get_card_checklists("card1")
    assert result == checklists


@respx.mock
def test_get_card_checklists_empty() -> None:
    respx.get(f"{BASE}/cards/card1/checklists").mock(return_value=httpx.Response(200, json=[]))
    result = get_card_checklists("card1")
    assert result == []
