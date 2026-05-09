from project.app import app


if __name__ == '__main__':
    from models.sqlModel import create_tables
    create_tables()
    
    app.run(host='0.0.0.0', port=8080)