HOST ?= 0.0.0.0
PORT ?= 1313
BASE_URL ?= http://192.168.28.6:1313

.PHONY: preview build clean

preview:
	hugo server --bind $(HOST) --port $(PORT) --baseURL $(BASE_URL) --appendPort=false --disableFastRender --cleanDestinationDir --noHTTPCache

build:
	hugo --minify --cleanDestinationDir

clean:
	rm -rf public resources/_gen
