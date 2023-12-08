import json
import os

import yaml
from mkdocs.plugins import BasePlugin


class TechDocsFrontmatterPlugin(BasePlugin):
  def on_post_build(self, config, **kwargs):
    data = {}
    site_dir = config["site_dir"]
    for page in config['pages'] or []:
      if not os.path.exists(page.file.abs_src_path):
        continue

      with open(page.file.abs_src_path, 'r', encoding='utf-8') as f:
        content = f.read()

      frontmatter = ""
      lines = content.splitlines()
      if lines[0].strip() == '---':
        lines.pop(0)
        for line in lines:
          if line.strip() == '---':
            break
          frontmatter += line + '\n'

      if frontmatter:
        try:
          data[page.file.url] = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
          self.log.warning(f"Failed to parse YAML frontmatter from {page.file.src_path}: {e}")
          continue

    if data:
      try:
        metadata = None
        with open(f"{site_dir}/techdocs_metadata.json", "r", encoding="utf-8") as fh:
          metadata = json.load(fh)
      except FileNotFoundError:
        metadata = {}
    
        metadata.setdefault("frontmatter", {}).update(data)
        try:
          with open(f"{site_dir}/techdocs_metadata.json", "w", encoding="utf-8") as fh:
            json.dump(metadata, fh)  
        except FileNotFoundError:
          self.log.warning(f"Failed to write frontmatter data to techdocs_metadata.json: {e}")
