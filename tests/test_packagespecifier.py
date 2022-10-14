import unittest

import conda_envfile


class Test(unittest.TestCase):
    """ """

    def test_build(self):

        v = conda_envfile.PackageSpecifier("foo=1.0=pypy")
        self.assertEqual(str(v), "foo=1.0=pypy")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "==1.0")
        self.assertEqual(str(v.range), "==1.0")
        self.assertEqual(v.build, "pypy")
        self.assertEqual(v.wildcard, None)

        v = conda_envfile.PackageSpecifier("foo=1.0")
        self.assertEqual(str(v), "foo =1.0")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "=1.0")
        self.assertEqual(str(v.range), ">=1.0.0, <1.1.0")
        self.assertEqual(v.build, None)
        self.assertEqual(v.wildcard, "=1.0")

        v = conda_envfile.PackageSpecifier("foo=1.*")
        self.assertEqual(str(v), "foo =1.*")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "=1.*")
        self.assertEqual(str(v.range), ">=1.0, <2.0")
        self.assertEqual(v.build, None)
        self.assertEqual(v.wildcard, "=1.*")

        v = conda_envfile.PackageSpecifier("foo *")
        self.assertEqual(str(v), "foo *")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "*")
        self.assertEqual(str(v.range), "")
        self.assertEqual(v.build, None)
        self.assertEqual(v.wildcard, "*")

        v = conda_envfile.PackageSpecifier("foo==1.0.0")
        self.assertEqual(str(v), "foo ==1.0.0")
        self.assertEqual(v.name, "foo")
        self.assertEqual(v.version, "==1.0.0")
        self.assertEqual(str(v.range), "==1.0.0")
        self.assertEqual(v.build, None)
        self.assertEqual(v.wildcard, "==1.0.0")

    def test_merge(self):

        tests = [
            ["foo ==1.2.0", "foo =1.2", "foo ==1.2.0"],
            ["foo >=1.2, <1.3", "foo =1.2", "foo =1.2"],
        ]

        for a, b, ret in tests:
            a = conda_envfile.PackageSpecifier(a)
            b = conda_envfile.PackageSpecifier(b)
            self.assertEqual(str(a + b), ret)
            self.assertEqual(str(b + a), ret)

    def test_PackageSpecifier_in(self):

        self.assertTrue("foo ==1.0" in conda_envfile.PackageSpecifier("foo ==1.0"))
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

        self.assertTrue("foo >=1.0, <2.0" not in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo >=1.0, <=2.0" not in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo >0.9, <2.0" not in conda_envfile.PackageSpecifier("foo =1.0"))
        self.assertTrue("foo >0.9, <=2.0" not in conda_envfile.PackageSpecifier("foo =1.0"))

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


if __name__ == "__main__":

    unittest.main(verbosity=2)
