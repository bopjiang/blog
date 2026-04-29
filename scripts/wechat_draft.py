#!/usr/bin/env python3
"""
Create a WeChat Official Account draft from a Hugo Markdown post.

The script intentionally has no third-party dependencies. It supports the
Markdown subset used by this blog well enough for draft creation, and keeps the
dangerous network action behind --create-draft.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.weixin.qq.com/cgi-bin"
INLINE_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_scalar(value: str) -> Any:
    value = strip_quotes(value)
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [strip_quotes(item.strip()) for item in inner.split(",")]
    return value


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text

    raw = text[4:end].splitlines()
    body = text[end + len("\n---\n") :]
    data: dict[str, Any] = {}
    current_key: str | None = None

    for line in raw:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and current_key:
            stripped = line.strip()
            if stripped.startswith("- "):
                data.setdefault(current_key, []).append(parse_scalar(stripped[2:]))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value:
            data[key] = parse_scalar(value)
        else:
            data[key] = []

    return data, body


def front_matter_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


def has_weixin_tag(data: dict[str, Any]) -> bool:
    return any(tag.lower() == "weixin" for tag in front_matter_list(data, "tags"))


def post_slug(path: Path, front_matter: dict[str, Any]) -> str:
    slug = front_matter.get("slug")
    if isinstance(slug, str) and slug:
        return slug
    return path.stem


def abs_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def local_image_path(post_path: Path, image_ref: str) -> Path | None:
    parsed = urllib.parse.urlparse(image_ref)
    if parsed.scheme in {"http", "https"}:
        return None
    clean = urllib.parse.unquote(parsed.path)
    if clean.startswith("/"):
        return Path("static") / clean.lstrip("/")
    return (post_path.parent / clean).resolve()


def replace_markdown_images(
    markdown: str,
    post_path: Path,
    access_token: str | None,
    create_draft: bool,
) -> tuple[str, list[str]]:
    uploaded: list[str] = []

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        src = match.group(2).strip()
        if urllib.parse.urlparse(src).scheme in {"http", "https"}:
            return match.group(0)
        image_path = local_image_path(post_path, src)
        if image_path is None:
            return match.group(0)
        if not image_path.exists():
            die(f"image not found: {src} resolved to {image_path}")
        if not create_draft:
            return f"![{alt}]({image_path})"
        if not access_token:
            die("missing access token while uploading inline image")
        url = upload_article_image(access_token, image_path)
        uploaded.append(str(image_path))
        return f"![{alt}]({url})"

    return INLINE_IMAGE_RE.sub(replace, markdown), uploaded


def inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"\u0000{len(placeholders) - 1}\u0000"

    def image_repl(match: re.Match[str]) -> str:
        alt = html.escape(match.group(1), quote=True)
        src = html.escape(match.group(2).strip(), quote=True)
        return stash(f'<img src="{src}" alt="{alt}" style="max-width:100%;height:auto;" />')

    def link_repl(match: re.Match[str]) -> str:
        label = inline_markdown(match.group(1))
        href = html.escape(match.group(2).strip(), quote=True)
        return stash(f'<a href="{href}">{label}</a>')

    text = INLINE_IMAGE_RE.sub(image_repl, text)
    text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m.group(1))}</code>"), text)
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)

    for i, value in enumerate(placeholders):
        escaped = escaped.replace(f"\u0000{i}\u0000", value)
    return escaped


def table_to_html(rows: list[str]) -> str:
    parsed_rows = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        parsed_rows.append(cells)
    if len(parsed_rows) < 2:
        return ""
    header = parsed_rows[0]
    body = parsed_rows[2:]
    out = ['<table style="border-collapse:collapse;width:100%;margin:16px 0;">']
    out.append("<thead><tr>")
    for cell in header:
        out.append(
            '<th style="border:1px solid #ddd;padding:6px;background:#f6f8fa;">'
            + inline_markdown(cell)
            + "</th>"
        )
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append('<td style="border:1px solid #ddd;padding:6px;">' + inline_markdown(cell) + "</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def markdown_to_wechat_html(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_rows: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(item.strip() for item in paragraph).strip()
            if text:
                out.append(f'<p style="line-height:1.8;margin:12px 0;">{inline_markdown(text)}</p>')
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            out.append('<ul style="padding-left:1.2em;line-height:1.8;margin:12px 0;">')
            for item in list_items:
                out.append(f"<li>{inline_markdown(item)}</li>")
            out.append("</ul>")
            list_items.clear()

    def flush_table() -> None:
        if table_rows:
            rendered = table_to_html(table_rows)
            if rendered:
                out.append(rendered)
            else:
                out.extend(table_rows)
            table_rows.clear()

    for line in lines:
        if line.startswith("```"):
            if in_code:
                code = html.escape("\n".join(code_lines))
                out.append(
                    '<pre style="background:#f6f8fa;border-radius:6px;padding:12px;'
                    'overflow-x:auto;font-size:13px;line-height:1.55;">'
                    f'<code>{code}</code></pre>'
                )
                in_code = False
                code_lang = ""
                code_lines.clear()
            else:
                flush_paragraph()
                flush_list()
                flush_table()
                in_code = True
                code_lang = line.strip("`").strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        if line.lstrip().startswith("|") and line.rstrip().endswith("|"):
            flush_paragraph()
            flush_list()
            table_rows.append(line)
            continue

        flush_table()
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = inline_markdown(heading.group(2).strip())
            if level <= 2:
                out.append(f'<h2 style="font-size:20px;margin:28px 0 12px;">{text}</h2>')
            else:
                out.append(f'<h3 style="font-size:17px;margin:22px 0 10px;">{text}</h3>')
            continue

        item = re.match(r"^\s*[-*]\s+(.+)$", line)
        if item:
            flush_paragraph()
            list_items.append(item.group(1).strip())
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    flush_table()

    return '<section style="font-size:15px;color:#24292f;">' + "\n".join(out) + "</section>"


def http_json(url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    method = "GET"
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        method = "POST"
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("errcode"):
        die(f"WeChat API error from {url}: {result}")
    return result


def multipart_upload(url: str, file_path: Path, field_name: str = "media") -> dict[str, Any]:
    boundary = f"----wechatdraft{int(time.time() * 1000)}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode()
    )
    body.extend(file_path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    request = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("errcode"):
        die(f"WeChat upload error from {url}: {result}")
    return result


def get_access_token(app_id: str, app_secret: str) -> str:
    query = urllib.parse.urlencode(
        {"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
    )
    result = http_json(f"{API_BASE}/token?{query}")
    token = result.get("access_token")
    if not token:
        die(f"access_token missing in response: {result}")
    return str(token)


def upload_article_image(access_token: str, file_path: Path) -> str:
    url = f"{API_BASE}/media/uploadimg?access_token={urllib.parse.quote(access_token)}"
    result = multipart_upload(url, file_path)
    image_url = result.get("url")
    if not image_url:
        die(f"image url missing in response: {result}")
    return str(image_url)


def upload_thumb(access_token: str, file_path: Path) -> str:
    url = f"{API_BASE}/material/add_material?access_token={urllib.parse.quote(access_token)}&type=thumb"
    result = multipart_upload(url, file_path)
    media_id = result.get("media_id")
    if not media_id:
        die(f"thumb media_id missing in response: {result}")
    return str(media_id)


def create_draft(access_token: str, article: dict[str, Any]) -> str:
    url = f"{API_BASE}/draft/add?access_token={urllib.parse.quote(access_token)}"
    result = http_json(url, {"articles": [article]})
    media_id = result.get("media_id")
    if not media_id:
        die(f"draft media_id missing in response: {result}")
    return str(media_id)


def first_present(data: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, list) and value:
            return str(value[0])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a WeChat draft from a Hugo Markdown post.")
    parser.add_argument("post", type=Path, help="Markdown post path")
    parser.add_argument("--create-draft", action="store_true", help="Call WeChat API and create a draft")
    parser.add_argument("--force", action="store_true", help="Bypass the required weixin tag check")
    parser.add_argument("--out", type=Path, default=Path("wechat/exported"), help="Dry-run output directory")
    parser.add_argument("--author", default=os.getenv("WECHAT_AUTHOR", ""), help="Article author")
    parser.add_argument("--thumb-media-id", default=os.getenv("WECHAT_THUMB_MEDIA_ID", ""))
    parser.add_argument("--cover", type=Path, default=Path(os.getenv("WECHAT_COVER_IMAGE", "")) if os.getenv("WECHAT_COVER_IMAGE") else None)
    args = parser.parse_args()

    post_path = args.post
    if not post_path.exists():
        die(f"post not found: {post_path}")

    front_matter, body = parse_front_matter(post_path.read_text(encoding="utf-8"))
    title = str(front_matter.get("title") or post_path.stem)
    description = str(front_matter.get("description") or "")

    if not args.force and not has_weixin_tag(front_matter):
        die(f"{post_path} does not have required tag: weixin")

    access_token: str | None = None
    if args.create_draft:
        app_id = os.getenv("WECHAT_APP_ID")
        app_secret = os.getenv("WECHAT_APP_SECRET")
        if not app_id or not app_secret:
            die("set WECHAT_APP_ID and WECHAT_APP_SECRET before using --create-draft")
        access_token = get_access_token(app_id, app_secret)

    body, uploaded_images = replace_markdown_images(body, post_path, access_token, args.create_draft)
    content = markdown_to_wechat_html(body)

    thumb_media_id = args.thumb_media_id
    cover_ref = first_present(front_matter, ["cover", "thumbnail", "image", "images"])
    cover_path = args.cover
    if cover_path is None and cover_ref:
        cover_path = local_image_path(post_path, cover_ref)
    if args.create_draft and not thumb_media_id:
        if not cover_path:
            die("set WECHAT_THUMB_MEDIA_ID, WECHAT_COVER_IMAGE, or front matter cover/image/images")
        if not cover_path.exists():
            die(f"cover image not found: {cover_path}")
        if not access_token:
            die("missing access token while uploading cover image")
        thumb_media_id = upload_thumb(access_token, cover_path)

    source_url = ""
    base_url = os.getenv("BLOG_BASE_URL", "")
    slug = post_slug(post_path, front_matter)
    if base_url and post_path.parts[:2] == ("content", "post"):
        date = str(front_matter.get("date") or "")
        match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)
        if match:
            source_url = abs_url(base_url, f"/post/{match.group(1)}/{match.group(2)}/{match.group(3)}/{slug}/")

    article = {
        "title": title,
        "author": args.author,
        "digest": description[:120],
        "content": content,
        "content_source_url": source_url,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }

    if args.create_draft:
        if not access_token:
            die("missing access token")
        media_id = create_draft(access_token, article)
        print(f"created WeChat draft: {media_id}")
        if uploaded_images:
            print(f"uploaded inline images: {len(uploaded_images)}")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    output = args.out / f"{slug}.html"
    output.write_text(content, encoding="utf-8")
    print(f"dry-run html: {output}")
    print(f"title: {title}")
    print(f"has weixin tag: {has_weixin_tag(front_matter)}")
    print("network: skipped; pass --create-draft to create a WeChat draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
