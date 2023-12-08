import json
import os
import tempfile
from unittest.mock import Mock

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import PluginCollection
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page

from modethirteen.mkdocs.metadata import TechDocsMetadataPlugin

@pytest.fixture
def mock_config():
  temp_dir = tempfile.mkdtemp()
  site_dir = os.path.join(temp_dir, "site")
  os.mkdir(site_dir)
  docs_dir = os.path.join(temp_dir, "docs")
  os.mkdir(docs_dir)
  options = {
    "site_dir": site_dir,
    "docs_dir": docs_dir,
    "plugins": PluginCollection([]),
  }
  config = MkDocsConfig()
  config.load_dict(options)
  return config

@pytest.fixture
def plugin_instance():
  return TechDocsMetadataPlugin()

def test_it_can_store_page_frontmatter_metadata_in_techdocs_metadata(mock_config, plugin_instance):

  # arrange
  docs_dir = mock_config["docs_dir"]
  site_dir = mock_config["site_dir"]
  foo = Page(
    "foo",
    File("foo.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  bar = Page(
    "bar",
    File("bar.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  baz = Page(
    "baz",
    File("baz.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  plugin_instance.log = Mock()
  with open(os.path.join(docs_dir, "foo.md"), "w", encoding="utf-8") as f:
    f.write("---\nkey1: value1\nkey2: value2\n---\n# foo")
  foo.read_source(config=mock_config)
  with open(os.path.join(docs_dir, "bar.md"), "w", encoding="utf-8") as f:
    f.write("# bar")
  bar.read_source(config=mock_config)
  with open(os.path.join(docs_dir, "baz.md"), "w", encoding="utf-8") as f:
    f.write("---\nkey3: value3\nkey4: value4\n---\n# baz")
  baz.read_source(config=mock_config)

  # act
  plugin_instance.on_page_markdown(page=foo, config=mock_config, markdown="markdown")
  plugin_instance.on_page_markdown(page=bar, config=mock_config, markdown="markdown")
  plugin_instance.on_page_markdown(page=baz, config=mock_config, markdown="markdown")
  plugin_instance.on_post_build(config=mock_config)

  # assert
  metadata_path = os.path.join(site_dir, "techdocs_metadata.json")
  assert os.path.exists(metadata_path)
  with open(metadata_path, "r", encoding="utf-8") as fh:
    metadata = json.load(fh)
    assert "pages" in metadata
    assert metadata["pages"] == [
      { "url": "foo/", "meta": { "key1": "value1", "key2": "value2" }},
      { "url": "baz/", "meta": { "key3": "value3", "key4": "value4" }}
    ]

if __name__ == "__main__":
  pytest.main()
