# WeChat Draft Publishing

Markdown remains the source of truth. Blog publishing still uses Hugo. WeChat publishing is an extra export path that creates a draft in the WeChat Official Account draft box.

Only posts tagged with `weixin` are eligible:

```yaml
tags:
  - weixin
```

Preview the generated WeChat HTML without network access:

```bash
make wechat-preview POST=content/post/example.md
```

Create a WeChat draft:

```bash
export WECHAT_APP_ID=...
export WECHAT_APP_SECRET=...
export WECHAT_THUMB_MEDIA_ID=...
make wechat-draft POST=content/post/example.md
```

If `WECHAT_THUMB_MEDIA_ID` is not set, provide a cover image with one of:

```bash
export WECHAT_COVER_IMAGE=static/images/cover.png
```

or front matter:

```yaml
cover: /images/cover.png
```

The script does not publish the draft. It only creates a draft in the WeChat draft box.
