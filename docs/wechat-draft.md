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
make wechat-draft POST=content/post/example.md
```

Cover priority:

1. `WECHAT_THUMB_MEDIA_ID`
2. `WECHAT_COVER_IMAGE`
3. front matter `cover`, `thumbnail`, `image`, or `images`
4. generated default PNG cover

If you want to provide an explicit cover image, use one of:

```bash
export WECHAT_COVER_IMAGE=static/images/cover.png
```

or front matter:

```yaml
cover: /images/cover.png
```

The WeChat API still needs a `thumb_media_id` for drafts. If no cover is configured, the script generates a simple default PNG cover and uploads it automatically.

The script does not publish the draft. It only creates a draft in the WeChat draft box.

## GitHub Actions

The `Create WeChat Drafts` workflow runs on pushes to `draft` and `wx` when posts or the publishing script change.

It only considers added or modified Markdown files under `content/post/`. Each file is still checked by `scripts/wechat_draft.py`, so posts without the `weixin` tag are skipped.

Configure these GitHub repository secrets:

```text
WECHAT_APP_ID
WECHAT_APP_SECRET
```

Optional repository variables:

```text
WECHAT_AUTHOR
BLOG_BASE_URL
```

You can also run the workflow manually with a single `post` input, such as:

```text
content/post/example.md
```
