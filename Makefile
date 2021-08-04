
develop:
	pip install -e .[dev,full]

demo:
	#cd tests && ./manage.py migrate && ./manage.py runserver
	cd tests/demoapp && ./manage.py testserver ../fixtures.json
clean:
	# cleaning
	@rm -fr dist '~build' .pytest_cache .coverage src/smart_admin.egg-info
	@find . -name __pycache__ -o -name .eggs | xargs rm -rf
	@find . -name "*.py?" -o -name ".DS_Store" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf

fullclean:
	@rm -rf .tox .cache
	$(MAKE) clean

docs:
	rm -fr ~build/docs/
	sphinx-build -n docs/ ~build/docs/

lint:
	@flake8 src/
	@isort src/


.PHONY: build docs


.build:
	docker build \
		-t saxix/smart-admin \
		-f docker/Dockerfile .
	docker images | grep ${DOCKER_IMAGE_NAME}

deploy:
	git checkout heroku
	git merge develop
	git push
	heroku pg:reset
	heroku run python tests/demoapp/manage.py collectstatic
	heroku run python tests/demoapp/manage.py migrate
	heroku run python tests/demoapp/manage.py loaddata tests/fixtures.json
	git checkout develop

