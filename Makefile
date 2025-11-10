.PHONY: help build up down logs clean test migrate shell

help:
	@echo "Theo CAD Platform - Development Commands"
	@echo ""
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Clean up containers and volumes"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make shell      - Open shell in API container"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec api pytest

migrate:
	docker-compose exec api alembic upgrade head

shell:
	docker-compose exec api /bin/bash

psql:
	docker-compose exec postgres psql -U theo -d theo_cad

redis-cli:
	docker-compose exec redis redis-cli

restart:
	docker-compose restart api worker

dev:
	docker-compose up
