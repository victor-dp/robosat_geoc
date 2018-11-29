check:
	pytest tests
	@echo ""
	@echo "==="
	black -l 125 --diff robosat_pink/*py robosat_pink/*/*.py
	@echo "==="
	@echo ""
	flake8 --max-line-length 125 --ignore=E203,E241,E226,E272,E261,E221,W503


black:
	black -l 125 robosat_pink/*py robosat_pink/*/*.py
