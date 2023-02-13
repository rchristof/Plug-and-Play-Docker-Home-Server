docker: docker-compose.yml
	docker-compose up -d

pipenv: Pipfile Pipfile.lock
	pipenv shell && pipenv install