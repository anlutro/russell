import os
import os.path
import re
import pytest
import russell.cli


@pytest.fixture(params=(True, False))
def russell_dir_variation(tmpdir, request):
    if request.param:
        return tmpdir.join("existing")
    return tmpdir.mkdir("newdir")


def test_setup_new_and_existing(russell_dir_variation):
    d = russell_dir_variation
    russell.cli.setup(str(d))
    assert d.join("config.py").check()
    assert d.join("requirements.txt").check()
    assert d.join(".gitignore").check()
    assert d.join("style.sass").check()
    assert d.join("pages").check()
    assert d.join("pages", "test-page.md").check()
    assert d.join("posts", "test-post.md").check()
    assert d.join("templates", "archive.html.jinja").check()
    assert d.join("templates", "index.html.jinja").check()
    assert d.join("templates", "layout.html.jinja").check()
    assert d.join("templates", "page.html.jinja").check()
    assert d.join("templates", "post.html.jinja").check()


@pytest.fixture(scope="module")
def russell_dir(request, tmpdir_factory):
    name = request.node.name
    name = re.sub(r"[\W]", "_", name)
    MAXVAL = 30
    if len(name) > MAXVAL:
        name = name[:MAXVAL]
    tmpdir = tmpdir_factory.mktemp(name, numbered=True)
    russell.cli.setup(str(tmpdir))
    os.chdir(str(tmpdir))
    return tmpdir


def test_new_page(russell_dir):
    russell.cli.new_page("New page")
    assert russell_dir.join("pages", "new-page.md").check()


def test_new_post(russell_dir):
    russell.cli.new_post("New post")
    assert russell_dir.join("posts", "new-post.md").check()
