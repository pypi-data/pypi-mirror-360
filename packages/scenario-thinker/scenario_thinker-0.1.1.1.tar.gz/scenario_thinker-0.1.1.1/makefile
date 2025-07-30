build2:
	rm -rf dist
	cp app.py src/st_preparation/files_to_copy_into_user/app.py
	cp -r services src/st_preparation/services
	python setup.py bdist_wheel
	python -m build	
push_test:
	python -m twine upload --repository testpypi dist/* --verbose
push_prod:
	python -m twine upload --repository pypi dist/*
pycache:
	git clean -df *pycache*