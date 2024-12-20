import json
import os
import tempfile
import logging
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
  plugin_instance.on_page_markdown(page=foo, markdown="markdown")
  plugin_instance.on_page_markdown(page=bar, markdown="markdown")
  plugin_instance.on_page_markdown(page=baz, markdown="markdown")
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

def test_it_can_merge_metadata_file_content(mock_config, plugin_instance):

  # arrange
  docs_dir = mock_config["docs_dir"]
  site_dir = mock_config["site_dir"]
  os.mkdir(os.path.join(docs_dir, "xyzzy"))
  foo = Page(
    "foo",
    File("xyzzy/foo.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  bar = Page(
    "bar",
    File("bar.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  os.mkdir(os.path.join(docs_dir, "foobar"))
  baz = Page(
    "baz",
    File("foobar/baz.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
    config={},
  )
  plugin_instance.log = Mock()
  with open(os.path.join(docs_dir, ".meta.yml"), "w", encoding="utf-8") as f:
    f.write("description: bazz")
  with open(os.path.join(docs_dir, "xyzzy", ".meta.yml"), "w", encoding="utf-8") as f:
    f.write("type: how-to\ntags:\n- plugh")
  with open(os.path.join(docs_dir, "foobar", ".meta.yml"), "w", encoding="utf-8") as f:
    f.write("tags:\n- typescript\ntype: reference")

  with open(os.path.join(docs_dir, "xyzzy", "foo.md"), "w", encoding="utf-8") as f:
    f.write("# foo")
  foo.read_source(config=mock_config)
  with open(os.path.join(docs_dir, "bar.md"), "w", encoding="utf-8") as f:
    f.write("---\nkey3: value3\nkey4: value4\n---\n# bar")
  bar.read_source(config=mock_config)
  with open(os.path.join(docs_dir, "foobar", "baz.md"), "w", encoding="utf-8") as f:
    f.write("---\ntags:\n- php\n---\n# baz")
  baz.read_source(config=mock_config)

  # act
  plugin_instance.on_pre_page(page=foo)
  plugin_instance.on_pre_page(page=bar)
  plugin_instance.on_pre_page(page=baz)

  # assert
  assert foo.meta == {
    "type": "how-to",
    "tags": ["plugh"],
    "description": "bazz"
  }
  assert bar.meta == {
    "key3": "value3",
    "key4": "value4",
    "description": "bazz"
  }
  assert baz.meta == {
    "type": "reference",
    "tags": ["php"],
    "description": "bazz"
  }

if __name__ == "__main__":
  pytest.main()
