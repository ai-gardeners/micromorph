build:
	docker build --no-cache -t micromorph .
sh:
	docker run -it -v .:/app micromorph sh
mm:
	python micromorph.py