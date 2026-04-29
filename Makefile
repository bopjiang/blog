HOST ?= 0.0.0.0
PORT ?= 1313
BASE_URL ?= http://192.168.28.6:1313

.PHONY: preview build clean wechat-preview wechat-draft

preview:
	hugo server --bind $(HOST) --port $(PORT) --baseURL $(BASE_URL) --appendPort=false --disableFastRender --cleanDestinationDir --noHTTPCache

build:
	hugo --minify --cleanDestinationDir

clean:
	rm -rf public resources/_gen

wechat-preview:
	python3 scripts/wechat_draft.py $(EXTRA_ARGS) $(POST)

wechat-draft:
	python3 scripts/wechat_draft.py --create-draft $(EXTRA_ARGS) $(POST)
