help:
	@echo "This Makefile rules are designed for RoboSat.pink devs and power-users."
	@echo "For plain user installation follow README.md instructions, instead."
	@echo ""
	@echo ""
	@echo " make install   To install, few Python dev tools and RoboSat.pink in editable mode."
	@echo "                So any further RoboSat.pink Python code modification will be usable at once,"
	@echo "                throught either rsp tools commands or robosat_pink.* modules."
	@echo ""
	@echo " make check     Launchs all tests, and tools doc updating."
	@echo "                Do it, at least, before sending a Pull Request."
	@echo ""
	@echo " make pink      Python code beautifier,"
	@echo "                as Pink is the new Black ^^"
	@echo ""


# Dev install
install:
	pip3 install pytest black flake8 twine
	pip3 install -e .


# Lauch all tests
check: ut it doc
	@echo "==================================================================================="
	@echo "All tests passed !"
	@echo "==================================================================================="


# Python code beautifier
pink:
	black -l 125 *.py robosat_pink/*.py robosat_pink/*/*.py


# Perform units tests, and linter checks
ut:
	@echo "==================================================================================="
	black -l 125 --check *.py robosat_pink/*.py robosat_pink/*/*.py
	@echo "==================================================================================="
	flake8 --max-line-length 125 --ignore=E203,E241,E226,E272,E261,E221,W503,E722
	@echo "==================================================================================="
	pytest tests


# Launch Integration Tests
it: it_pre it_train it_post


# Integration Tests: Data Preparation
it_pre:
	@echo "==================================================================================="
	rm -rf it
	rsp cover --zoom 18 --type bbox 4.8,45.7,4.83,45.73  it/cover
	rsp download --rate 20 --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' it/cover it/images
	wget -nc -O it/lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&BBOX=4.79,45.69,4.84,45.74&outputFormat=application/json; subtype=geojson' | true
	rsp rasterize --geojson it/lyon_roofprint.json --config config.toml it/cover it/labels
	wget -O it/lyon.pbf http://datapink.tools/rsp/it/lyon.pbf 
	rsp extract --type building it/lyon.pbf it/osm_lyon_footprint.json
	rsp rasterize --geojson it/lyon_roofprint.json --config config.toml it/cover it/labels_osm
	rm -rf it/training it/validation
	mkdir it/training it/validation
	rsp cover --type dir it/images --splits 70,30 it/training/cover it/validation/cover
	rsp subset --dir it/images --filter it/training/cover it/training/images
	rsp subset --dir it/labels --filter it/training/cover it/training/labels
	rsp subset --dir it/images --filter it/validation/cover it/validation/images
	rsp subset --dir it/labels --filter it/validation/cover it/validation/labels


# Integration Tests: Training
it_train:
	@echo "==================================================================================="
	rsp train --config config.toml --batch_size 2 --epochs 3 --dataset it it/pth
	rsp train --config config.toml --batch_size 2 --epochs 5 --resume --checkpoint it/pth/checkpoint-00003-of-00003.pth --dataset it it/pth


# Integration Tests: Post Training
it_post:
	@echo "==================================================================================="
	rsp export --checkpoint it/pth/checkpoint-00005-of-00005.pth --config config.toml --type jit it/pth/export.jit
	rsp export --checkpoint it/pth/checkpoint-00005-of-00005.pth --config config.toml --type onnx it/pth/export.onnx
	rsp predict --config config.toml --batch_size 4 --checkpoint it/pth/checkpoint-00005-of-00005.pth it/images it/masks
	rsp compare --images it/images it/labels it/masks --mode stack --labels it/labels --masks it/masks --config config.toml it/compare
	rsp compare --mode list --labels it/labels --maximum_qod 75 --minimum_fg 5 --masks it/masks --config config.toml --geojson it/compare/tiles.json
	rsp vectorize --type building --config config.toml it/masks it/vector.json


# Documentation generation (tools and config file)
doc:
	@echo "==================================================================================="
	@echo "# RoboSat.pink tools documentation" > docs/tools.md
	@for tool in `ls robosat_pink/tools/[^_]*py | sed -e 's#.*/##g' -e 's#.py##'`; do \
		echo "Doc generation: $$tool"; 						  \
		echo "## rsp $$tool" >> docs/tools.md; 				  	  \
		echo '```'           >> docs/tools.md; 				  	  \
		rsp $$tool -h        >> docs/tools.md; 				  	  \
		echo '```'           >> docs/tools.md; 				  	  \
	done
	@echo "Doc generation: config.toml"
	@echo "## config.toml"        > docs/config.md; 			  	  \
	echo '```'                    >> docs/config.md; 			  	  \
	cat config.toml               >> docs/config.md; 			  	  \
	echo '```'                    >> docs/config.md;
	@echo "Doc generation: Makefile"
	@echo "## Makefile"           > docs/makefile.md; 			  	  \
	echo '```'                    >> docs/makefile.md; 			  	  \
	make --no-print-directory     >> docs/makefile.md; 			  	  \
	echo '```'                    >> docs/makefile.md;


# Send a release on PyPI
pypi: check
	rm -rf dist RoboSat.pink.egg-info
	python3 setup.py sdist
	twine upload dist/* -r pypi
