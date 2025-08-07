DC = sudo docker compose

all: drop_all start_all logs_all

start_all:
	$(DC) up --build -d

drop_all:
	$(DC) down

logs_all:
	$(DC) logs -f

format:
	poetry run ruff format src/ --config pyproject.toml

lint:
	poetry run ruff check src/ --config pyproject.toml --fix