from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.config.defaults import MkDocsConfig
import json
import yaml
import os


class TechDocsMetadataPlugin(BasePlugin):
    def __init__(self):
        self.data = []

    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, **kwargs
    ) -> str:
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
                        for key, value in meta_data.items():
                            if (
                                key in merged_meta
                                and isinstance(value, list)
                                and isinstance(merged_meta[key], list)
                            ):
                                merged_meta[key] = value + merged_meta[key]
                            elif key not in merged_meta:
                                merged_meta[key] = value
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir

        # merge the metadata into the page's frontmatter
        if merged_meta:
            page_meta = page.meta or {}
            for key, value in merged_meta.items():
                if key in page_meta:
                    if isinstance(value, list) and isinstance(page_meta[key], list):
                        page_meta[key] = value + page_meta[key]
                else:
                    page_meta[key] = value
            page.meta = page_meta

        # Traverse up the directory tree to locate mkdocs-awesome-page .pages files
        # and collect titles and directory paths as page parents
        parents = []
        current_dir = file_dir
        docs_dir = os.path.abspath(config.docs_dir)
        while current_dir:
            pages_file_path = os.path.join(current_dir, ".pages")
            if os.path.isfile(pages_file_path):
                with open(pages_file_path, "r") as pages_file:
                    pages_data = yaml.safe_load(pages_file)
                    if pages_data:
                        if (
                            current_dir == file_dir
                            and pages_data.get("collapse") == True
                        ):
                            parent_dir = os.path.dirname(current_dir)
                            if parent_dir == current_dir:
                                break
                            current_dir = parent_dir
                            continue
                        relative_path = os.path.relpath(current_dir, docs_dir)
                        title = pages_data.get("title", "")
                        if relative_path != "." and not title:
                            title = os.path.basename(current_dir)
                        parents.append({"title": title, "url": f"{relative_path}/"})

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir or current_dir == docs_dir:
                break
            current_dir = parent_dir

        self.data.append(
            {
                "title": page.title,
                "url": page.file.url,
                "meta": page.meta or {},
                "parents": parents[::-1],  # Reverse the list to get the correct order
            }
        )

        return markdown

    def on_post_build(self, config: MkDocsConfig, **kwargs) -> None:
        site_dir = config["site_dir"]
        if self.data:
            try:
                metadata = None
                with open(
                    f"{site_dir}/techdocs_metadata.json", "r", encoding="utf-8"
                ) as fh:
                    metadata = json.load(fh)
            except FileNotFoundError:
                metadata = {}

            metadata.setdefault("pages", []).extend(self.data)
            try:
                with open(
                    f"{site_dir}/techdocs_metadata.json", "w", encoding="utf-8"
                ) as fh:
                    json.dump(metadata, fh)
            except FileNotFoundError:
                self.log.warning(
                    f"Failed to write page frontmatter metadata to techdocs_metadata.json: {e}"
                )
