from mkdocs.plugins import BasePlugin
import json
import yaml
import os

class TechDocsMetadataPlugin(BasePlugin):
  def __init__(self):
    self.data = []

  def on_pre_page(self, page, **kwargs):
    file_path = page.file.abs_src_path
    file_dir = os.path.dirname(file_path)

    # traverse up the directory tree to locate and merge .meta.yml files
    merged_meta = {}
    current_dir = file_dir
    while current_dir:
      meta_file_path = os.path.join(current_dir, ".meta.yml")
      if os.path.isfile(meta_file_path):
        with open(meta_file_path, "r") as meta_file:
          meta_data = yaml.safe_load(meta_file)
          if meta_data:
            merged_meta.update(meta_data)
      parent_dir = os.path.dirname(current_dir)
      if parent_dir == current_dir:
        break
      current_dir = parent_dir

    # merge the metadata into the page's frontmatter
    if merged_meta:
      page_meta = page.meta or {}
      page.meta = {**merged_meta, **page_meta}

  def on_page_markdown(self, markdown, page, **kwargs):
    if page.meta:
      self.data.append({ "url": page.file.url, "meta": page.meta })
    return markdown

  def on_post_build(self, config, **kwargs):
    site_dir = config["site_dir"]
    if self.data:
      try:
        metadata = None
        with open(f"{site_dir}/techdocs_metadata.json", "r", encoding="utf-8") as fh:
          metadata = json.load(fh)
      except FileNotFoundError:
        metadata = {}
    
      metadata.setdefault("pages", []).extend(self.data)
      try:
        with open(f"{site_dir}/techdocs_metadata.json", "w", encoding="utf-8") as fh:
          json.dump(metadata, fh)  
      except FileNotFoundError:
        self.log.warning(f"Failed to write page frontmatter metadata to techdocs_metadata.json: {e}")
