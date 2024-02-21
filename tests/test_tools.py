import pytest

import conda_envfile


def test_unique():
    dependencies = [
        [
            ["foo =1.2", "foo >=1.2", "foo <1.3", "foo >1.0", "foo <2.0"],
            ["foo =1.2"],
        ],
        [
            ["foo =1.2", "foo >1.0", "foo <=1.3", "foo >0.9", "foo <=1.4"],
            ["foo =1.2"],
        ],
        [
            ["foo =1.2", "foo <2.0", "foo <1.3", "foo >0.0", "foo >=0.5"],
            ["foo =1.2"],
        ],
        [
            ["foo >=1.2", "foo <=1.2"],
            ["foo =1.2"],
        ],
        [
            ["foo >=1.2", "foo <=1.2", "foo ==1.2.0"],
            ["foo ==1.2.0"],
        ],
        [
            ["foo", "foo", "foo"],
            ["foo"],
        ],
        [
            ["foo", "foo >1.0", "foo >0.9", "foo >=0.8"],
            ["foo >1.0"],
        ],
        [
            ["foo", "foo <1.0", "foo <2.0"],
            ["foo <1.0"],
        ],
        [
            ["foo", "foo >1.0, <2.0", "foo >0.9, <3.0", "foo >=1.0, <=2.1", "foo >=1.0, <=2.0"],
            ["foo >1.0, <2.0"],
        ],
        [
            ["foo", "foo >=1.0, <=2.0", "foo >0.9, <3.0", "foo >=0.9, <=3.0"],
            ["foo >=1.0, <=2.0"],
        ],
        [
            ["foo *", "foo"],
            ["foo *"],
        ],
        [
            ["foo *", "foo >1.0", "foo =1.*", "foo <2.0", "foo <=3.1", "foo >0.1, <3.0"],
            ["foo >1.0, <2.0"],
        ],
        [
            ["foo =1.*", "foo >0.9", "foo", "foo <=2.0", "foo >0.1, <3.0", "foo *", "foo =1.*"],
            ["foo =1.*"],
        ],
        [
            ["foo =1.2.*", "foo", "foo <=2.0.0", "foo >1.0.1, <2.1.0", "foo =1.2.*", "foo *"],
            ["foo =1.2.*"],
        ],
        [
            ["foo =1.2.*", "foo >1.2.0", "foo >1.1.0"],
            ["foo >1.2.0, <1.3.0"],
        ],
    ]

    for deps, expect in dependencies:
        for _ in range(len(deps)):
            deps.append(deps.pop(0))
            nospace = [i.replace(" ", "") for i in deps]
            assert list(map(str, conda_envfile.unique(*deps))) == expect
            assert list(map(str, conda_envfile.unique(*nospace))) == expect

    illegal = [
        ["foo >1.2.0", "foo <1.2.0", "foo", "foo *", "foo =1.2.*"],
        ["foo =1.2.*", "foo >=1.3.0", "foo 1.*"],
        ["foo =1.2.*", "foo <1.2.0", "foo", "foo *"],
        ["foo >=1.2.0, <1.3.0", "foo >=1.3.0", "foo"],
        ["foo >=1.2.0, <2", "foo >=1.3.0", "foo >=2.0.0", "foo"],
    ]

    for deps in illegal:
        for _ in range(len(deps)):
            deps.append(deps.pop(0))
            with pytest.raises(ValueError):
                conda_envfile.unique(*deps)
            with pytest.raises(ValueError):
                conda_envfile.unique(*[i.replace(" ", "") for i in deps])


def test_remove():
    assert conda_envfile.remove(["foo", "bar"], "bar") == ["foo"]
    assert conda_envfile.remove(["foo *", "bar *"], "bar") == ["foo *"]
    assert conda_envfile.remove(["foo =1.*", "bar =1.*"], "bar") == ["foo =1.*"]
    assert conda_envfile.remove(["foo >1.0", "bar >1.0"], "bar") == ["foo >1.0"]


def test_contains():
    requirements = ["foo >1.0", "bar >=2.0"]
    installed = ["foo=2.0=generic", "bar=3.0=generic", "other"]
    assert conda_envfile.contains(requirements, installed)

    installed = ["foo=2.0=generic", "bar=1.0=generic", "other"]
    assert not conda_envfile.contains(requirements, installed)


def test_restrict():
    ret = list(map(str, conda_envfile.restrict(["foo", "bar"], ["foo >1.0"])))
    assert ret == ["foo >1.0", "bar"]

    ret = conda_envfile.restrict(["foo", "bar"], ["foo >1.0"])
    assert ret == list(map(conda_envfile.PackageSpecifier, ["foo >1.0", "bar"]))
