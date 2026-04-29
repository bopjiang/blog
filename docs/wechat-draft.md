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

## GitHub Actions

The `Create WeChat Drafts` workflow runs on pushes to `draft` and `wx` when posts or the publishing script change.

It only considers added or modified Markdown files under `content/post/`. Each file is still checked by `scripts/wechat_draft.py`, so posts without the `weixin` tag are skipped.

Configure these GitHub repository secrets:

```text
WECHAT_APP_ID
WECHAT_APP_SECRET
WECHAT_THUMB_MEDIA_ID
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
