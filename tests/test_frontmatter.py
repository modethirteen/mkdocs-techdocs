import json
import os
import tempfile
from unittest.mock import Mock

import pytest
import yaml
from mkdocs.config import config_options
from mkdocs.plugins import PluginCollection
from mkdocs.structure.files import File
from mkdocs.structure.pages import Page

from modethirteen.mkdocs.frontmatter import TechDocsFrontmatterPlugin


@pytest.fixture
def mock_config():
  temp_dir = tempfile.mkdtemp()
  site_dir = os.path.join(temp_dir, "site")
  os.mkdir(site_dir)
  docs_dir = os.path.join(temp_dir, "docs")
  os.mkdir(docs_dir)
  return {
    "site_dir": site_dir,
    "docs_dir": docs_dir,
    "plugins": PluginCollection([]),
    "pages": [
      Page(
        "foo",
        File("foo.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
        config={},
      ),
      Page(
        "bar",
        File("bar.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
        config={},
      ),
      Page(
        "baz",
        File("baz.md", src_dir=docs_dir, dest_dir=site_dir, use_directory_urls=True),
        config={},
      ),
    ],
  }

@pytest.fixture
def plugin_instance():
  return TechDocsFrontmatterPlugin()

def test_it_can_store_frontmatter_in_techdocs_metadata(mock_config, plugin_instance):

  # arrange
  plugin_instance.log = Mock()
  with open(os.path.join(mock_config["docs_dir"], "foo.md"), "w", encoding="utf-8") as f:
    f.write("---\nkey1: value1\nkey2: value2\n---\n")
  with open(os.path.join(mock_config["docs_dir"], "baz.md"), "w", encoding="utf-8") as f:
    f.write("---\nkey3: value3\nkey4: value4\n---\n")

  # act
  plugin_instance.on_post_build(mock_config)

  # assert
  metadata_path = os.path.join(mock_config["site_dir"], "techdocs_metadata.json")
  assert os.path.exists(metadata_path)
  with open(metadata_path, "r", encoding="utf-8") as fh:
    metadata = json.load(fh)
    assert "frontmatter" in metadata
    assert metadata["frontmatter"]["foo/"] == { "key1": "value1", "key2": "value2" }
    assert "bar/" not in metadata["frontmatter"]
    assert metadata["frontmatter"]["baz/"] == { "key3": "value3", "key4": "value4" }

def test_it_can_handle_empty_page_list(plugin_instance):

  # arrange
  mock_config = {
    "site_dir": "site_dir",
    "docs_dir": "docs_dir",
    "plugins": PluginCollection([]),
    "pages": None,
  }

  # act
  plugin_instance.on_post_build(mock_config)

if __name__ == '__main__':
  pytest.main()
