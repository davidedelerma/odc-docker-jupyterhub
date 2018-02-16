all: datacube-notebook

datacube-notebook:
	make -C datacube-notebook

docker-bootstrap:
	@echo "Checking/creating networks"
	@docker network inspect jupyterhub >/dev/null 2>/dev/null || docker network create jupyterhub
	@echo "Checking/creating volumes"
	@docker volume inspect datacube-config-volume >/dev/null 2>/dev/null || docker volume create datacube-config-volume

update-config-volume: docker-bootstrap
	@echo "Populating skeleton.tgz from user_folder"
	@(cd user_folder/; tar cz .) | docker run --rm -i -v datacube-config-volume:/data busybox sh -c "cat > /data/skeleton.tgz"

clean-orphans:
	@echo "Cleaning up orphaned images"
	@docker images | grep "<none>" | awk '{print $3}' | xargs docker rmi

.PHONY: all datacube-notebook docker-bootstrap update-config-volume
