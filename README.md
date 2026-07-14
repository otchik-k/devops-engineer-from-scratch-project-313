### Hexlet tests and linter status:
[![Actions Status](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions)
[![Lint with Ruff](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions/workflows/lint.yml/badge.svg)](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions/workflows/lint.yml)
[![Run Tests](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions/workflows/tests.yml/badge.svg)](https://github.com/otchik-k/devops-engineer-from-scratch-project-313/actions/workflows/tests.yml)


Данный набор кода на Python представляет собой реализацию учебного проекта **"Деплой приложения на PaaS"** курса **"DevOps-инженер с нуля"** на Hexlet<br>

В проекте используется следующие зависимости:<br>
	"flask>=3.1.3", <br>
    "flask-cors>=6.0.5",<br>
    "gunicorn>=26.0.0",<br>
    "make>=0.1.6.post2",<br>
    "psycopg2-binary>=2.9.12",<br>
    "pytest>=9.0.3",<br>
    "pytest-mock>=3.15.1",<br>
    "ruff>=0.15.12",<br>
    "sqlmodel>=0.0.38",<br>


Для работы бекенда нужен PostgreSQL<br>
Строка подключения к БД задается через переменную окружения DATABASE_URL<br>

Для локального запуска бекенда используйте команду:<br>
	make run<br>

Для запуска фронт+бек используйте команду:<br>
    make start<br>

Ссылка на проект в Render:<br> 
https://devops-engineer-from-scratch-project-313-cgbt.onrender.com/#/links