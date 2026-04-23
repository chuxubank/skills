# Attachments Reference (附件)

Tools for uploading and downloading attachments in Feishu Project work items.

## Tool Map

| Intent | Tool | Key Params |
|--------|------|------------|
| 上传附件（获取上传URL） | `upload_file` | `project_key`, `work_item_id`, `file_name`, `mime_type`, `size`, `resource_type`, `field_key`(optional) |
| 获取附件下载URL | `get_download_url` | `file_url`, `project_key`(optional), `work_item_id`(optional) |

## Upload Workflow

### 1. Get Upload URL and Sign

Call `upload_file` to get an upload URL and sign token:

```
upload_file(
    project_key="<key>",
    work_item_id="<id>",
    file_name="screenshot.png",
    mime_type="image/png",
    size=102400,
    resource_type=15,
    field_key="field_xxx"
)
```

**`resource_type` values:**

| Scene | Value |
|-------|-------|
| 附件字段 | `15` |
| 富文本字段中的图片 | `16` |
| 评论附件 | `13` |
| 评论图片 | `14` |

- For comment attachments/images, `field_key` is not required.
- Returns `url`, `sign`, and `is_multipart` (whether multipart upload is needed).

### 2. Upload the File via curl

Use the returned URL and sign to upload:

```bash
curl -X POST "<returned_url>" \
  -H "X-Meego-File-Sign: <returned_sign>" \
  -H "Content-Type: <mime_type>" \
  --data-binary @<local_file>
```

- The URL contains `:part_number` — replace with `0` for non-multipart uploads.
- **Do NOT write scripts** — use curl directly.

### 3. Multipart Upload (Large Files)

When `is_multipart` is `true`:

1. The response includes `part_index` entries with `start_byte` and `end_byte`.
2. For each part, replace `:part_number` in the URL with the part index.
3. Upload each part sequentially.
4. The last part must include all remaining bytes.
5. The final part upload returns the file `url` and `token`.

### 4. Using Uploaded Files

After upload, you get a file `url` and `token`. Use them in:

**Attachment fields (`file` type):**
```json
[{
    "name": "screenshot.png",
    "type": "image/png",
    "size": "99.4KB",
    "fileToken": "<token>"
}]
```

**Rich text fields (`multi-text`) — images:**
```markdown
![image_name](<file_url>)<!--<file_token> -->
```

**Comments — images:**
Same markdown format as rich text. Or pass `file_token` to `add_comment`.

## Download Workflow

### Get Download URL

Convert an attachment URL (from a file field, comment, or rich text) to a downloadable URL:

```
get_download_url(
    file_url="<attachment_url>",
    project_key="<key>",
    work_item_id="<id>"
)
```

Returns:
- `url` — the download URL
- `sign` — the file sign (add as `X-Meego-File-Sign` header)
- `is_multipart` — whether the file needs multipart download

For multipart downloads, use `part_index` with `start_byte` and `end_byte` to download
each segment, replacing `:part_number` in the URL.

```bash
curl -X POST "<download_url>" \
  -H "X-Meego-File-Sign: <sign>" \
  -o <output_file>
```
