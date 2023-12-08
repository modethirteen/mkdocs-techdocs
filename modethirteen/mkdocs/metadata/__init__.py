import json

from mkdocs.plugins import BasePlugin

class TechDocsMetadataPlugin(BasePlugin):
  def __init__(self):
    self.data = []

  def on_page_markdown(self, markdown, page, config, **kwargs):
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
