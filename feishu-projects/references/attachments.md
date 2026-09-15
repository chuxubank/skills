# Attachments

| Intent | Tool |
|---|---|
| Obtain upload URL/sign | `feishu_upload_file` |
| Obtain download URL/sign | `feishu_get_download_url` |

Resource types: attachment field `15`, rich-text field `16`, comment attachment `13`, comment
image `14`. `field_key` applies to attachment fields; comment files/images omit it. Uploads for a
new work item also require `work_item_type` when no item ID exists.

## Upload

1. Call `feishu_upload_file` with space, scene, file metadata, and item/type locator.
2. Use the returned URL and `X-Meego-File-Sign` with direct `curl`; do not generate an upload script.
3. Replace `:part_number` with `0` for a non-multipart upload.
4. For multipart upload, process returned parts in order, using each `part_index`, `start_byte`, and
   `end_byte`; the last part includes all remaining bytes. Keep `Content-Type` equal to `mime_type`.
5. Capture the final file URL/token.

```bash
curl -X POST '<upload-url>' \
  -H 'X-Meego-File-Sign: <sign>' \
  -H 'Content-Type: <mime-type>' \
  --data-binary '@<local-file>'
```

Use the token in a `file` field object, or embed a rich-text/comment image as:

```markdown
![name](<file-url>)<!--<file-token> -->
```

A comment attachment can instead be sent as `file_token` in `feishu_add_comment`.

## Download

`feishu_get_download_url` requires `file_url`, `project_key`, and `work_item_id`. Perform a GET with
the returned sign header. For multipart results, fetch each returned part/range and assemble in
order.

```bash
curl -L '<download-url>' -H 'X-Meego-File-Sign: <sign>' -o '<output-file>'
```
