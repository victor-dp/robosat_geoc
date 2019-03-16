all:
	@echo "This Makefile purpose is for RoboSat.pink devs and maintainers."
	@echo "For INSTALL concern give a look on README.md"

check_all: check it doc

check:
	pytest tests
	@echo ""
	@echo "==="
	black -l 125 --check *.py robosat_pink/*.py robosat_pink/*/*.py
	@echo "==="
	@echo ""
	flake8 --max-line-length 125 --ignore=E203,E241,E226,E272,E261,E221,W503,E722
	@echo "==="


black:
	black -l 125 *.py robosat_pink/*.py robosat_pink/*/*.py

doc:
	@echo "# RoboSat.pink tools documentation" > docs/tools.md
	@for tool in `ls robosat_pink/tools/[^_]*py | sed -e 's#.*/##g' -e 's#.py##'`; do \
		echo "Doc generation: $$tool"; 						  \
		echo "## rsp $$tool" >> docs/tools.md; 				  	  \
		echo '```'           >> docs/tools.md; 				  	  \
		rsp $$tool -h        >> docs/tools.md; 				  	  \
		echo '```'           >> docs/tools.md; 				  	  \
	done
	@echo "Doc generation: config.toml"
	@echo "## config.toml" > docs/config.md; 				  	  \
	echo '```'           >> docs/config.md; 				  	  \
	cat config.toml      >> docs/config.md; 				  	  \
	echo '```'           >> docs/config.md;
	

it: it_preparation it_train it_post

it_preparation:
	rm -rf it
	rsp cover --zoom 18 --type bbox 4.8,45.7,4.83,45.73  it/cover
	rsp download --rate 20 --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' --web_ui it/cover it/images
	rsp download --rate 20 --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' --web_ui it/cover it/images
	wget -nc -O it/lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&BBOX=4.79,45.69,4.84,45.74&outputFormat=application/json; subtype=geojson' | true
	rsp rasterize --config config.toml --geojson it/lyon_roofprint.json --web_ui it/cover it/labels
	wget -O it/ra.pbf http://download.geofabrik.de/europe/france/rhone-alpes-latest.osm.pbf
	osmium extract -b 4.8,45.7,4.83,45.73 -s smart -o it/lyon.pbf it/ra.pbf
	rsp extract --type building it/lyon.pbf it/osm_lyon_footprint.json
	rsp rasterize --config config.toml --geojson it/lyon_roofprint.json --web_ui it/cover it/labels_osm
	rm -rf it/training it/validation
	mkdir it/training it/validation
	cat it/cover | sort -R > it/cover.shuffled
	head -n 500 it/cover.shuffled > it/training/cover
	tail -n 236 it/cover.shuffled > it/validation/cover
	rsp subset --web_ui --dir it/images --cover it/training/cover --out it/training/images
	rsp subset --web_ui --dir it/labels --cover it/training/cover --out it/training/labels
	rsp subset --web_ui --dir it/images --cover it/validation/cover --out it/validation/images
	rsp subset --web_ui --dir it/labels --cover it/validation/cover --out it/validation/labels

it_train:
	rsp train --config config.toml --workers 2 --epochs 3 --batch_size 2 --dataset it it/pth
	rsp train --config config.toml --workers 2 --batch_size 2 --resume --checkpoint it/pth/checkpoint-00003-of-00003.pth --epochs 5 --dataset it it/pth

it_post:
	rsp predict --config config.toml --workers 2 --batch_size 4 --checkpoint it/pth/checkpoint-00005-of-00005.pth --web_ui it/images it/masks
	rsp compare --images it/images it/labels it/masks --mode stack --labels it/labels --masks it/masks --config config.toml --web_ui it/compare
	rsp compare --mode list --labels it/labels --maximum_qod 70 --minimum_fg 5 --masks it/masks --config config.toml --geojson it/tiles.json
	rsp vectorize --type building --config config.toml it/masks it/vector.json

install:
	pip3 install -e .

install-dev:
	sudo apt install -y osmium-tool
	sudo pip3 install pytest twine black flake8


pypi: check
	rm -rf dist RoboSat.pink.egg-info
	python3 setup.py sdist
	twine upload dist/* -r pypi
