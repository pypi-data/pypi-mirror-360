import tempfile
from reqbuddy import get_requirement, find_requirement

def write_temp_file(content: str) -> str:
    fd, path = tempfile.mkstemp(text=True)
    with open(path, "w") as f:
        f.write(content)
    return path

def test_get_requirement_basic():
    path = write_temp_file("flask\nrequests")
    result = get_requirement(path)
    assert result == ["flask", "requests"]

def test_get_strip_versions():
    path = write_temp_file("flask==2.0\nrequests>=2.0")
    result = get_requirement(path, strip=True)
    assert result == ["flask", "requests"]

def test_get_deduplicate():
    path = write_temp_file("flask\nflask\nrequests")
    result = get_requirement(path, deduplicate=True)
    assert result == ["flask", "requests"]

def test_find_requirement_basic():
    result = find_requirement()
    assert isinstance(result, list)
    assert any("pip" in r for r in result)

def test_find_strip_versions():
    result = find_requirement(strip=True)
    assert all("==" not in r for r in result)