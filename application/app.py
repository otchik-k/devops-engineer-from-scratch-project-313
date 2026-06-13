import os

import signal

import sys

#from config import DATABASE_URL

from links_repository import LinksRepository

from table_model import create_tables

import psycopg2


from flask import (
    Flask,
    request,
    jsonify
)


def create_app():
    app = Flask(__name__)
    
    print('Инициализация приложения')
    #os.environ['DATABASE_URL'] = "postgresql://hexlet:12345@localhost:5432/stud_db"
    db_connect = os.environ['DATABASE_URL']
    conn = psycopg2.connect(db_connect)
    repo = LinksRepository(conn)
    create_tables()
    
    
    def shutdown_app():
        print("Завершение работы приложения")
        conn.close()
    
    
    def signal_handler(signum, frame):
        shutdown_app()
        sys.exit(0)
    
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    
    @app.teardown_appcontext
    def cleanup(error):
        pass
    

    @app.route('/')
    def hello():
        return 'Project started from Flask on port 8080!'


    @app.route('/ping', methods=['GET'])
    def ping():
        return 'pong'


    @app.route('/api/links', methods=['GET'])
    def get_links():
        raw_data = repo.select_all_links()
        links = [dict(row) for row in raw_data] 
        return jsonify({"status": "success", "data": links}), 200


    @app.route('/api/links', methods=['POST'])
    def post_links():
        if not request.is_json:
            return jsonify({"error": "Требуется Content-Type: application/json"}), 415
            
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "Некорректный JSON-формат"}), 400
            
        original_url = data.get('original_url')
        short_name = data.get('short_name')

        if not original_url or not short_name:
            return jsonify({"error": "Поля 'short_name' и 'original_url' обязательны"}), 422
        
        print(f'original_url={original_url}')
        print(f'short_name={short_name}')
        result = repo.insert_data(original_url, short_name)
        return jsonify({"status": "success", "short_url": result}), 201


    @app.route('/api/links/<id>', methods=['GET'])
    def get_link_for_id(id):
        raw_data = repo.select_link_for_id(id)
        link = [dict(row) for row in raw_data]
        return jsonify({"status": "success", "data": link}), 200


    @app.route('/api/links/<id>', methods=['PUT'])
    def put_link_for_id(id):
        if not request.is_json:
            return jsonify({"error": "Требуется Content-Type: application/json"}), 415
            
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({"error": "Некорректный JSON-формат"}), 400
            
        original_url = data.get('original_url')
        short_name = data.get('short_name')
        if not original_url or not short_name:
            return jsonify({"error": "Поле 'name' обязательно"}), 422
        
        repo.update_link_for_id(id, original_url, short_name)
        raw_data = repo.select_link_for_id(id)
        link = [dict(row) for row in raw_data]
        return jsonify({"status": "success", "data": link}), 200
        

    @app.route('/api/links/<id>', methods=['DELETE'])
    def delete_link_for_id(id):
        repo.delete_link_for_id(id)
        return 'No Content', 204
        

    @app.errorhandler(404)
    def not_found(error):
        return "Oops! Error 404", 404
        
        
    return app


app = create_app()