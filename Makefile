.PHONY: dev api dashboard install test lint clean docker

install:
	pip install -e .
	cd dashboard && npm install

dev: api dashboard

api:
	uvicorn api.app:app --reload --port 8000

dashboard:
	cd dashboard && npm run dev

build:
	cd dashboard && npm run build

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check pgc_explorer/ api/
	cd dashboard && npx tsc --noEmit

clean:
	rm -rf __pycache__ *.egg-info dist build
	rm -rf dashboard/dist dashboard/node_modules

docker:
	docker compose up --build
