build:
	docker build -t micromorph .
sh:
	docker run -it -v .:/app micromorph sh
mm:
	docker run -it -v .:/app micromorph python micromorph.py