import unittest

import conda_envfile


class Test(unittest.TestCase):
    """ """

    def test_conda_envfile(self):

        self.assertEqual(conda_envfile.unique("foo", "foo"), ["foo"])
        self.assertEqual(conda_envfile.unique("foo", "foo >1.0"), ["foo >1.0"])
        self.assertEqual(conda_envfile.unique("foo", "foo <1.0"), ["foo <1.0"])
        self.assertEqual(conda_envfile.unique("foo", "foo >1.0, <2.0"), ["foo >1.0, <2.0"])
        self.assertEqual(conda_envfile.unique("foo", "foo"), ["foo"])
        self.assertEqual(conda_envfile.unique("foo >1.0", "foo"), ["foo >1.0"])
        self.assertEqual(conda_envfile.unique("foo <1.0", "foo"), ["foo <1.0"])
        self.assertEqual(conda_envfile.unique("foo >1.0, <2.0", "foo"), ["foo >1.0, <2.0"])

        self.assertEqual(conda_envfile.unique("foo *", "foo"), ["foo *"])
        self.assertEqual(conda_envfile.unique("foo *", "foo >1.0"), ["foo >1.0"])
        self.assertEqual(conda_envfile.unique("foo *", "foo <1.0"), ["foo <1.0"])
        self.assertEqual(conda_envfile.unique("foo *", "foo >1.0, <2.0"), ["foo >1.0, <2.0"])
        self.assertEqual(conda_envfile.unique("foo", "foo *"), ["foo *"])
        self.assertEqual(conda_envfile.unique("foo >1.0", "foo *"), ["foo >1.0"])
        self.assertEqual(conda_envfile.unique("foo <1.0", "foo *"), ["foo <1.0"])
        self.assertEqual(conda_envfile.unique("foo >1.0, <2.0", "foo *"), ["foo >1.0, <2.0"])

        self.assertEqual(conda_envfile.unique("foo =1.2.*", "foo >1.2.0"), ["foo >1.2.0, <1.3.0"])
        self.assertEqual(conda_envfile.unique("foo >1.2.0", "foo =1.2.*"), ["foo >1.2.0, <1.3.0"])
        self.assertEqual(conda_envfile.unique("foo =1.2.*", "foo =1.2.*"), ["foo =1.2.*"])

        self.assertEqual(conda_envfile.unique("foo >=1.2.0", "foo >=1.3.0"), ["foo >=1.3.0"])
        self.assertEqual(conda_envfile.unique("foo >1.3", "foo >=1.3"), ["foo >1.3"])
        self.assertEqual(
            conda_envfile.unique("foo >1.3, <1.5", "foo >=1.3, <=1.5"), ["foo >1.3, <1.5"]
        )
        self.assertEqual(conda_envfile.unique("foo >=1.2", "foo <=1.2"), ["foo =1.2"])
        self.assertEqual(conda_envfile.unique("foo >=1.2", "foo =1.2"), ["foo =1.2"])
        self.assertEqual(conda_envfile.unique("foo =1.2", "foo >=1.2"), ["foo =1.2"])
        self.assertEqual(conda_envfile.unique("foo =1.2", "foo <1.3"), ["foo =1.2"])
        self.assertEqual(conda_envfile.unique("foo <1.3", "foo =1.2"), ["foo =1.2"])

        with self.assertRaises(ValueError):
            conda_envfile.unique("foo >1.2.0", "foo <1.2.0")

        with self.assertRaises(ValueError):
            conda_envfile.unique("foo =1.2.*", "foo >=1.3.0")

        with self.assertRaises(ValueError):
            conda_envfile.unique("foo =1.2.*", "foo <1.2.0")

        with self.assertRaises(ValueError):
            conda_envfile.unique("foo >=1.2.0, <1.3.0", "foo >=1.3.0")

        with self.assertRaises(ValueError):
            conda_envfile.unique("foo >=1.2.0, <2", "foo >=1.3.0", "foo >=2.0.0")
