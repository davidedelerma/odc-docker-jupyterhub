all: datacube-notebook

geo-base: Dockerfile.geo
	docker build -t $@ --file $< .

geo-jupyter: Dockerfile.geo-jupyter geo-base
	docker build -t $@ --file $< .

datacube-notebook: Dockerfile.datacube geo-jupyter
	docker build -t $@ --file $< .

.PHONY: all geo-jupyter geo-base datacube-notebook
