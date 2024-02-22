import pytest

import conda_envfile


def test_setter():
    v = conda_envfile.PackageSpecifier("foo >=1.0.0")
    v.version = ">=2.0.0"
    assert str(v) == "foo >=2.0.0"


def test_norm():
    tests = [
        ["foo <= 1.0.0", "foo <=1.0.0"],
        ["foo < 1.0.0", "foo <1.0.0"],
        ["foo >= 1.0.0", "foo >=1.0.0"],
        ["foo > 1.0.0", "foo >1.0.0"],
        ["foo = 1.0", "foo =1.0"],
        ["foo = 1.*", "foo =1.*"],
        ["foo == 1.0", "foo ==1.0"],
        ["foo *", "foo *"],
        ["foo > 1.0, < 2.0", "foo >1.0, <2.0"],
    ]
    for a, b in tests:
        v = conda_envfile.PackageSpecifier(a)
        assert str(v) == b


def test_build():
    v = conda_envfile.PackageSpecifier("foo=1.0=pypy")
    assert str(v) == "foo=1.0=pypy"
    assert v.name == "foo"
    assert v.version == "==1.0"
    assert str(v.range) == "==1.0"
    assert v.build == "pypy"
    assert v.wildcard is None

    v = conda_envfile.PackageSpecifier("foo=1.0")
    assert str(v) == "foo =1.0"
    assert v.name == "foo"
    assert v.version == "=1.0"
    assert str(v.range) == ">=1.0.0, <1.1.0"
    assert v.build is None
    assert v.wildcard == "=1.0"

    v = conda_envfile.PackageSpecifier("foo=1.*")
    assert str(v) == "foo =1.*"
    assert v.name == "foo"
    assert v.version == "=1.*"
    assert str(v.range) == ">=1.0, <2.0"
    assert v.build is None
    assert v.wildcard == "=1.*"

    v = conda_envfile.PackageSpecifier("foo *")
    assert str(v) == "foo *"
    assert v.name == "foo"
    assert v.version == "*"
    assert str(v.range) == ""
    assert v.build is None
    assert v.wildcard == "*"

    v = conda_envfile.PackageSpecifier("foo==1.0.0")
    assert str(v) == "foo ==1.0.0"
    assert v.name == "foo"
    assert v.version == "==1.0.0"
    assert str(v.range) == "==1.0.0"
    assert v.build is None
    assert v.wildcard == "==1.0.0"


def test_merge():
    tests = [
        ["foo ==1.2.0", "foo =1.2", "foo ==1.2.0"],
        ["foo >=1.2, <1.3", "foo =1.2", "foo =1.2"],
    ]

    for a, b, ret in tests:
        a = conda_envfile.PackageSpecifier(a)
        b = conda_envfile.PackageSpecifier(b)
        assert str(a + b) == ret
        assert str(b + a) == ret


def test_PackageSpecifier_in():
    assert "foo ==1.0" in conda_envfile.PackageSpecifier("foo ==1.0")
    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo >=1.0, <=1.0" in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo =1.0" not in conda_envfile.PackageSpecifier("foo =2.0")
    assert "foo >0.9" not in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo <1.1" not in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo >0.9, <1.1" not in conda_envfile.PackageSpecifier("foo =1.0")

    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0")
    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9")

    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0, <2.0")
    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0, <=2.0")
    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9, <2.0")
    assert "foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9, <=2.0")

    assert "foo >=1.0, <2.0" not in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo >=1.0, <=2.0" not in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo >0.9, <2.0" not in conda_envfile.PackageSpecifier("foo =1.0")
    assert "foo >0.9, <=2.0" not in conda_envfile.PackageSpecifier("foo =1.0")

    assert "foo =1.0" not in conda_envfile.PackageSpecifier("foo >1.0")
    assert "foo =1.0" not in conda_envfile.PackageSpecifier("foo <1.0")

    assert "foo <1.0" in conda_envfile.PackageSpecifier("foo <1.0")
    assert "foo <0.9" in conda_envfile.PackageSpecifier("foo <1.0")
    assert "foo <0.9" in conda_envfile.PackageSpecifier("foo <=1.0")
    assert "foo <=0.9" in conda_envfile.PackageSpecifier("foo <1.0")
    assert "foo <=0.9" in conda_envfile.PackageSpecifier("foo <=1.0")
    assert "foo <=1.0" not in conda_envfile.PackageSpecifier("foo <1.0")
    assert "foo <1.0" not in conda_envfile.PackageSpecifier("foo <=0.9")
    assert "foo >=1.0" not in conda_envfile.PackageSpecifier("foo >1.0")
    assert "foo >1.0" not in conda_envfile.PackageSpecifier("foo >=1.1")
    assert "foo" not in conda_envfile.PackageSpecifier("foo <1.0")

    assert "foo >=0.5, <=1.0" in conda_envfile.PackageSpecifier("foo <2.0")
    assert "foo >0.5, <=1.0" in conda_envfile.PackageSpecifier("foo <2.0")
    assert "foo >0.5, <1.0" in conda_envfile.PackageSpecifier("foo <1.0")
    assert "foo <1.0" not in conda_envfile.PackageSpecifier("foo >0.5, <1.0")
    assert "foo <1.0" not in conda_envfile.PackageSpecifier("foo >0.5, <=1.0")
    assert "foo <1.0" not in conda_envfile.PackageSpecifier("foo >=0.5, <1.0")
    assert "foo <1.0" not in conda_envfile.PackageSpecifier("foo >=0.5, <=1.0")

    assert "foo *" in conda_envfile.PackageSpecifier("foo")
    assert "foo =1.*" in conda_envfile.PackageSpecifier("foo >=1.0, <2.0")
    assert "foo =1.*" not in conda_envfile.PackageSpecifier("foo >1.0, <2.0")


def test_interpret():
    interpret = [
        "foo",
        "foo >1.0",
        "foo >=1.0",
        "foo >=1.0, <2.0",
        "foo >=1.0, <=2.0",
        "foo >1.0, <2.0",
        "foo >1.0, <=2.0",
        "foo =1.0.*",
    ]

    for name in interpret:
        assert str(conda_envfile.PackageSpecifier(name)) == name
        assert str(conda_envfile.PackageSpecifier(name.replace(" ", ""))) == name

    assert str(conda_envfile.PackageSpecifier("foo >=1.2.0, <=1.2.0")) == "foo =1.2.0"

    illegal = [
        "foo >1.2.0, <1.2.0",
        "foo >=1.2.0, <1.2.0",
        "foo >1.2.0, <=1.2.0",
        "foo >=1.3.0, <=1.2.0",
    ]

    for dep in illegal:
        with pytest.raises(ValueError):
            conda_envfile.PackageSpecifier(dep)
