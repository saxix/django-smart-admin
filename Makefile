
develop:
	python -m venv .venv
	.venv/bin/pip install -e .[dev,full]

demo:
	cd tests/demoapp && ./manage.py testserver ../fixtures.json

clean:
	# cleaning
	@rm -fr dist '~build' .pytest_cache .coverage src/smart_admin.egg-info build
	@find . -name __pycache__ -o -name .eggs | xargs rm -rf
	@find . -name "*.py?" -o -name ".DS_Store" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf

fullclean:
	@rm -rf .tox .cache
	$(MAKE) clean

docs:
	rm -fr ~build/docs/
	sphinx-build -n docs/ ~build/docs/

lint:
	@flake8 src/ tests/
	@isort src/ tests/


.PHONY: build docs


.build:
	docker build \
		-t saxix/smart-admin \
		-f docker/Dockerfile .
	docker images | grep ${DOCKER_IMAGE_NAME}

heroku:
	@git checkout heroku
	@git merge develop -m "merge develop"
	@git push heroku heroku:master
	@git checkout develop
	@echo "check demo at https://django-smart-admin.herokuapp.com/"

heroku-reset: heroku
	heroku pg:reset --confirm django-smart-admin
	heroku run python tests/demoapp/manage.py migrate
	heroku run python tests/demoapp/manage.py collectstatic --noinput

