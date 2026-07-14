import os

import signal

import sys

from typing import Optional

from links_repository import LinksRepository

from table_model import create_tables

from flask_cors import CORS

import psycopg2

from flask import Flask, request, jsonify


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

    print('Инициализация приложения')
    DATABASE_URL = os.environ['DATABASE_URL']
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    conn = psycopg2.connect(DATABASE_URL)
    repo = LinksRepository(conn)
    create_tables()

    def shutdown_app():
        print("Завершение работы приложения")
        try:
            conn.close()
        except Exception:
            pass

    def signal_handler(signum, frame):
        shutdown_app()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    def parse_range_param(range_str: Optional[str]):
        if not range_str:
            return None
        cleaned = range_str.strip().strip('[]')
        if ',' in cleaned:
            parts = cleaned.split(',')
        elif ':' in cleaned:
            parts = cleaned.split(':')
        else:
            return None

        if len(parts) != 2:
            return None

        try:
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            if start < 0 or end < 0 or start > end:
                return None
            return start, end
        except ValueError:
            return None

    class API:
        @app.route('/')
        def hello():
            return 'Project started from Flask on port 8080!'

        @app.route('/ping', methods=['GET'])
        def ping():
            return 'pong'

        @app.route('/api/links', methods=['GET'])
        def get_links():
            range_param = request.args.get('range')
            range_values = parse_range_param(range_param)
            total_count = repo.get_total_links_count()

            if range_values is None:
                raw_data = repo.select_all_links()
                start = 0
                end = max(0, total_count - 1)
            else:
                start, end_requested = range_values
                end = min(end_requested, total_count - 1)
                if start > end:
                    raw_data = []
                    start = end + 1  # чтобы корректно посчитать Content-Range
                else:
                    raw_data = repo.select_links_from_range((start, end))

            links = [dict(row) for row in raw_data]
            content_range = f"links {start}-{end}/{total_count}"
            response = jsonify(links)
            response.headers['Content-Range'] = content_range
            return response, 200

        @app.route('/api/links', methods=['POST'])
        def post_links():
            if not request.is_json:
                return jsonify({"detail": "Требуется Content-Type: application/json"}), 415

            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"detail": {"error": "Некорректный JSON-формат"}}), 400

            original_url = data.get('original_url')
            short_name = data.get('short_name')

            if not original_url or not short_name:
                return jsonify({
                    "detail": "Поля 'short_name' и 'original_url' обязательны"
                }), 422

            result = repo.insert_data(original_url, short_name)
            if result is None:
                return jsonify({"detail": "Ошибка при сохранении ссылки"}), 500
            return jsonify(result), 201


        @app.route('/api/links/<id>', methods=['GET'])
        def get_link_for_id(id: str):
            try:
                link_id = int(id)
            except (ValueError, TypeError):
                return jsonify({"detail": "Некорректный ID"}), 400

            link = repo.select_link_for_id(link_id)
            if link is None:
                return jsonify({"detail": "Ссылка не найдена"}), 404
            return jsonify(link), 200

        @app.route('/api/links/<id>', methods=['PUT'])
        def put_link_for_id(id: str):
            if not id.isdigit():
                return jsonify({"detail": "Некорректный ID"}), 400

            if not request.is_json:
                return jsonify({"detail": {"error": "Требуется Content-Type: application/json"}}), 422

            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"detail": {"error": "Некорректный JSON-формат"}}), 422

            original_url = data.get('original_url')
            short_name = data.get('short_name')

            if not original_url or not short_name:
                return jsonify({
                "detail": {"error": "Поля 'original_url' и 'short_name' обязательны"}
            }), 422

            link_id = int(id)
            # сначала проверим, существует ли запись
            existing = repo.select_link_for_id(link_id)
            if existing is None:
                return jsonify({"detail": "Ссылка не найдена"}), 404

            repo.update_link_for_id(link_id, original_url, short_name)
            updated = repo.select_link_for_id(link_id)
            if updated is None:
                return jsonify({"detail": "Ошибка обновления"}), 500
            return jsonify(updated), 200

        @app.route('/api/links/<id>', methods=['DELETE'])
        def delete_link_for_id(id: str):
            if not id.isdigit():
                return jsonify({"detail": "Некорректный ID"}), 400

            link_id = int(id)
            existing = repo.select_link_for_id(link_id)
            if existing is None:
                return jsonify({"detail": "Ссылка не найдена"}), 404

            repo.delete_link_for_id(link_id)
            return '', 204

        @app.errorhandler(404)
        def not_found(error):
            return jsonify({"detail": "Ресурс не найден"}), 404

    return app


app = create_app()
