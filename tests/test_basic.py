import unittest

from packaging.version import Version

import conda_envfile


class Test(unittest.TestCase):
    """ """

    def test_build(self):

        v = conda_envfile.PackageSpecifier("foo=1.0=pypy")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "=1.0")
        self.assertEqual(v.version_range, "=1.0")
        self.assertEqual(v.build, "pypy")
        self.assertEqual(v.wildcard, "")

        v = conda_envfile.PackageSpecifier("foo=1.0")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "=1.0")
        self.assertEqual(v.version_range, "=1.0")
        self.assertEqual(v.build, "")
        self.assertEqual(v.wildcard, "")

        v = conda_envfile.PackageSpecifier("foo=1.*")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "=1.*")
        self.assertEqual(v.version_range, ">=1.0, <2.0")
        self.assertEqual(v.build, "")
        self.assertEqual(v.wildcard, "=1.*")

        v = conda_envfile.PackageSpecifier("foo *")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "*")
        self.assertEqual(v.version_range, "")
        self.assertEqual(v.build, "")
        self.assertEqual(v.wildcard, "*")

    def test_PackageSpecifier_has_same_name(self):

        self.assertTrue(conda_envfile.PackageSpecifier("foo =1.0").has_same_name("foo"))
        self.assertTrue(~conda_envfile.PackageSpecifier("foo =1.0").has_same_name("bar"))

    def test_PackageSpecifier_in(self):

        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo >=1.0, <=1.0" in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo =1.0" not in conda_envfile.PackageSpecifier("foo =2.0"))
        self.assertTrue("foo >0.9" not in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo <1.1" not in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo >0.9, <1.1" not in conda_envfile.PackageSpecifier("foo =1.0"))

        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0"))
        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9"))

        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0, <2.0"))
        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >=1.0, <=2.0"))
        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9, <2.0"))
        self.assertTrue("foo =1.0" in conda_envfile.PackageSpecifier("foo >0.9, <=2.0"))

        self.assertTrue("foo =1.0" not in conda_envfile.PackageSpecifier("foo >1.0"))
        self.assertTrue("foo =1.0" not in conda_envfile.PackageSpecifier("foo <1.0"))

        self.assertTrue("foo <1.0" in conda_envfile.PackageSpecifier("foo <1.0"))
        self.assertTrue("foo <0.9" in conda_envfile.PackageSpecifier("foo <1.0"))
        self.assertTrue("foo <0.9" in conda_envfile.PackageSpecifier("foo <=1.0"))
        self.assertTrue("foo <=0.9" in conda_envfile.PackageSpecifier("foo <1.0"))
        self.assertTrue("foo <=0.9" in conda_envfile.PackageSpecifier("foo <=1.0"))
        self.assertTrue("foo <=1.0" not in conda_envfile.PackageSpecifier("foo <1.0"))
        self.assertTrue("foo <1.0" not in conda_envfile.PackageSpecifier("foo <=0.9"))
        self.assertTrue("foo >=1.0" not in conda_envfile.PackageSpecifier("foo >1.0"))
        self.assertTrue("foo >1.0" not in conda_envfile.PackageSpecifier("foo >=1.1"))
        self.assertTrue("foo" not in conda_envfile.PackageSpecifier("foo <1.0"))

        self.assertTrue("foo >=0.5, <=1.0" in conda_envfile.PackageSpecifier("foo <2.0"))
        self.assertTrue("foo >0.5, <=1.0" in conda_envfile.PackageSpecifier("foo <2.0"))
        self.assertTrue("foo >0.5, <1.0" in conda_envfile.PackageSpecifier("foo <1.0"))
        self.assertTrue("foo <1.0" not in conda_envfile.PackageSpecifier("foo >0.5, <1.0"))
        self.assertTrue("foo <1.0" not in conda_envfile.PackageSpecifier("foo >0.5, <=1.0"))
        self.assertTrue("foo <1.0" not in conda_envfile.PackageSpecifier("foo >=0.5, <1.0"))
        self.assertTrue("foo <1.0" not in conda_envfile.PackageSpecifier("foo >=0.5, <=1.0"))

        self.assertTrue("foo *" in conda_envfile.PackageSpecifier("foo"))
        self.assertTrue("foo =1.*" in conda_envfile.PackageSpecifier("foo >=1.0, <2.0"))
        self.assertTrue("foo =1.*" not in conda_envfile.PackageSpecifier("foo >1.0, <2.0"))

    def test_PackageSpecifier_in_overload(self):

        self.assertTrue(Version("1.0") in conda_envfile.PackageSpecifier("foo =1.0"))

    def test_interpret(self):

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
            self.assertEqual(str(conda_envfile.PackageSpecifier(name)), name)
            self.assertEqual(str(conda_envfile.PackageSpecifier(name.replace(" ", ""))), name)

        self.assertEqual(
            str(conda_envfile.PackageSpecifier("foo >=1.2.0, <=1.2.0")),
            "foo =1.2.0",
        )

        illegal = [
            "foo >1.2.0, <1.2.0",
            "foo >=1.2.0, <1.2.0",
            "foo >1.2.0, <=1.2.0",
            "foo >=1.3.0, <=1.2.0",
        ]

        for dep in illegal:
            with self.assertRaises(ValueError):
                conda_envfile.PackageSpecifier(dep)

    def test_unique(self):

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
                self.assertEqual(conda_envfile.unique(*deps), expect)
                self.assertEqual(conda_envfile.unique(*[i.replace(" ", "") for i in deps]), expect)

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
                with self.assertRaises(ValueError):
                    conda_envfile.unique(*deps)
                with self.assertRaises(ValueError):
                    conda_envfile.unique(*[i.replace(" ", "") for i in deps])

    def test_remove(self):

        self.assertEqual(conda_envfile.remove(["foo", "bar"], "bar"), ["foo"])
        self.assertEqual(conda_envfile.remove(["foo *", "bar *"], "bar"), ["foo *"])
        self.assertEqual(conda_envfile.remove(["foo =1.*", "bar =1.*"], "bar"), ["foo =1.*"])
        self.assertEqual(conda_envfile.remove(["foo >1.0", "bar >1.0"], "bar"), ["foo >1.0"])

    def test_restrict(self):

        self.assertEqual(conda_envfile.restrict(["foo", "bar"], ["foo >1.0"]), ["foo >1.0", "bar"])


if __name__ == "__main__":

    unittest.main(verbosity=2)
