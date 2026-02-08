build:
	docker build --no-cache -t micromorph .
sh:
	docker run -it -v .:/app micromorph sh
mm:
	docker run -it -v .:/app micromorph mm