import pytest
from unittest.mock import patch, MagicMock
import app

@pytest.fixture
def client():
    with patch('app.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        with patch('app.LinksRepository') as MockRepoClass:
            mock_repo = MagicMock()
            MockRepoClass.return_value = mock_repo
            
            with patch('app.create_tables'):
                test_app = app.create_app()
                test_app.config['TESTING'] = True
                
                test_app.mock_repo = mock_repo 
                
                with test_app.test_client() as client:
                    yield client, mock_repo

def test_ping(client):
    c, _ = client
    response = c.get('/ping')
    assert response.status_code == 200
    assert response.data == b'pong'

def test_get_links(client):
    c, mock_repo = client
    mock_repo.select_all_links.return_value = [
        {'id': 1, 'original_url': 'http://google.com', 'short_name': 'gl', 'short_url': 'http://s/gl/1'}
    ]
    
    response = c.get('/api/links')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['short_name'] == 'gl'

def test_post_links_success(client):
    c, mock_repo = client
    mock_repo.insert_data.return_value = "http://short.ly/test/1"
    
    payload = {
        "original_url": "http://example.com",
        "short_name": "test"
    }
    
    response = c.post('/api/links', json=payload)
    assert response.status_code == 201
    assert response.json['status'] == 'success'
    mock_repo.insert_data.assert_called_once_with("http://example.com", "test")

def test_post_links_missing_fields(client):
    c, _ = client
    payload = {"original_url": "http://example.com"}
    
    response = c.post('/api/links', json=payload)
    assert response.status_code == 422
    assert "обязательны" in response.json['error']

def test_post_links_invalid_json(client):
    c, _ = client
    response = c.post('/api/links', data="not a json")
    assert response.status_code == 415
    assert "Content-Type" in response.json['error']

def test_put_link_for_id(client):
    c, mock_repo = client
    mock_repo.select_link_for_id.return_value = [
        {'id': 1, 'original_url': 'http://new.com', 'short_name': 'new', 'short_url': 'http://s/new/1'}
    ]
    
    payload = {
        "original_url": "http://new.com",
        "short_name": "new"
    }
    
    response = c.put('/api/links/1', json=payload)
    assert response.status_code == 200
    assert response.json['data'][0]['short_name'] == 'new'
    mock_repo.update_link_for_id.assert_called_once_with('1', 'http://new.com', 'new')

def test_delete_link_for_id(client):
    c, mock_repo = client
    
    response = c.delete('/api/links/1')
    assert response.status_code == 204
    mock_repo.delete_link_for_id.assert_called_once_with('1')

def test_not_found(client):
    c, _ = client
    response = c.get('/nonexistent_route')
    assert response.status_code == 404
    assert response.data == b"Oops! Error 404"


@patch('app.parse_range_param')
def test_get_links_without_range(mock_parse, client):
    c, mock_repo = client
    
    # Настраиваем моки
    mock_parse.return_value = None  # parse_range_param вернул None
    mock_repo.get_total_links_count.return_value = 5
    mock_repo.select_all_links.return_value = [
        {'id': 1, 'original_url': 'http://a.com', 'short_name': 'a', 'short_url': '...'}
    ]
    
    response = c.get('/api/links')
    
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert len(response.json['data']) == 1
    
    # Проверяем заголовок Content-Range: start=0, end=5-1=4, total=5
    assert response.headers.get('Content-Range') == 'links 0-4/5'
    
    # Должен вызваться метод получения всех записей
    mock_repo.select_all_links.assert_called_once()
    mock_repo.select_links_from_range.assert_not_called()


@patch('app.parse_range_param')
def test_get_links_with_valid_range(mock_parse, client):
    c, mock_repo = client
    
    mock_parse.return_value = (0, 9)  # Запросили первые 10 записей (с 0 по 9)
    mock_repo.get_total_links_count.return_value = 20  # Всего в базе 20 записей
    mock_repo.select_links_from_range.return_value = [{'id': i} for i in range(10)]
    
    response = c.get('/api/links?range=0-9')
    
    assert response.status_code == 200
    # end = min(9, 20-1) = 9. Заголовок: links 0-9/20
    assert response.headers.get('Content-Range') == 'links 0-9/20'
    
    # Проверяем, что в репозиторий ушел корректный кортеж
    mock_repo.select_links_from_range.assert_called_once_with((0, 9))


@patch('app.parse_range_param')
def test_get_links_with_range_exceeding_total(mock_parse, client):
    c, mock_repo = client
    
    mock_parse.return_value = (15, 25)  # Запросили с 15 по 25
    mock_repo.get_total_links_count.return_value = 20  # Но всего в базе только 20 (индексы 0-19)
    mock_repo.select_links_from_range.return_value = []
    
    response = c.get('/api/links?range=15-25')
    
    assert response.status_code == 200
    # end = min(25, 20-1) = 19. Заголовок: links 15-19/20
    assert response.headers.get('Content-Range') == 'links 15-19/20'
    
    # В репозиторий должен уйти уже обрезанный диапазон (15, 19)
    mock_repo.select_links_from_range.assert_called_once_with((15, 19))