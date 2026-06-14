import pytest

from unittest.mock import MagicMock, patch

from links_repository import LinksRepository

@pytest.fixture
def mock_db():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor

def test_insert_data_success(mock_db):
    conn, cursor = mock_db
    # Имитируем ответ от RETURNING id
    cursor.fetchone.return_value = {'id': 42}
    
    repo = LinksRepository(conn)
    with patch('links_repository.DOMEN_FOR_SHORT_URL', 'http://short.ly'):
        result = repo.insert_data("http://example.com", "mylink")
    
    assert result == "http://short.ly/mylink/42"
    assert cursor.execute.call_count == 2
    conn.commit.assert_called_once()


def test_insert_data_rollback_on_error(mock_db):
    conn, cursor = mock_db
    cursor.execute.side_effect = Exception("DB Error")
    
    repo = LinksRepository(conn)
    result = repo.insert_data("http://example.com", "mylink")
    
    assert result is None
    conn.rollback.assert_called_once()


def test_select_all_links(mock_db):
    conn, cursor = mock_db
    expected_data = [{
        'id': 1,
        'original_url': 'http://a.com',
        'short_name': 'a',
        'short_url': 'http://s/a/1'
        }]
    cursor.fetchall.return_value = expected_data
    
    repo = LinksRepository(conn)
    result = repo.select_all_links()
    
    assert result == expected_data
    cursor.execute.assert_called_once_with('SELECT id, original_url, short_name, short_url FROM links')


def test_delete_link_for_id(mock_db):
    conn, cursor = mock_db
    repo = LinksRepository(conn)
    repo.delete_link_for_id(5)
    
    cursor.execute.assert_called_once_with(
        "\n                DELETE FROM links\n                WHERE id = %s\n            ", 
        (5,)
    )
    conn.commit.assert_called_once()