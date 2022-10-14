import unittest

import conda_envfile


class Test(unittest.TestCase):
    """ """

    def test_VersionRange(self):

        tests = [
            [{}, ""],
            [dict(less="1.0"), "<1.0"],
            [dict(greater="0.0", less="1.0"), ">0.0, <1.0"],
            [dict(greater="0.0", greater_equal="0.0", less="1.0"), ">0.0, <1.0"],
            [dict(greater="0.0", greater_equal="0.1", less="1.0"), ">=0.1, <1.0"],
            [dict(greater="0.0", less="1.0", less_equal="0.9"), ">0.0, <=0.9"],
            [dict(greater="0.0", less="1.0", less_equal="1.0"), ">0.0, <1.0"],
            [dict(greater_equal="0.0", less="1.0"), ">=0.0, <1.0"],
            [dict(greater_equal="0.0", less_equal="1.0"), ">=0.0, <=1.0"],
            [dict(greater_equal="1.0", less_equal="1.0"), "==1.0"],
            [dict(greater_equal="0.0", less_equal="3.0", equal="2.0"), "==2.0"],
        ]

        for range, expect in tests:
            v = conda_envfile.VersionRange(**range)
            self.assertEqual(str(v), expect)

    def test_VersionRange_illegal(self):

        tests = [
            dict(less="1.0", greater="1.0"),
            dict(greater="1.2.0", less="1.2.0"),
            dict(greater_equal="1.2.0", less="1.2.0"),
            dict(greater="1.2.0", less_equal="1.2.0"),
            dict(greater_equal="1.3.0", less_equal="1.2.0"),
        ]

        for range in tests:
            with self.assertRaises(ValueError):
                conda_envfile.VersionRange(**range)

    def test_VersionRange_merge(self):

        p = conda_envfile.VersionRange(less="1.0")
        s = conda_envfile.VersionRange(less="2.0")
        self.assertEqual(str(p + s), "<1.0")
        self.assertEqual(str(s + p), "<1.0")

    def test_VersionRange_in(self):

        tests = [
            [dict(equal="1.0"), True, dict(equal="1.0")],
            [dict(greater_equal="1.0", less_equal="1.0"), True, dict(equal="1.0")],
            [dict(equal="1.0"), False, dict(equal="2.0")],
            [dict(greater="0.9"), False, dict(equal="1.0")],
            [dict(less="1.1"), False, dict(equal="1.0")],
            [dict(greater="0.9", less="1.1"), False, dict(equal="1.0")],
            [dict(equal="1.0"), True, dict(greater_equal="1.0")],
            [dict(equal="1.0"), True, dict(greater="0.9")],
            [dict(equal="1.0"), True, dict(greater_equal="1.0", less="2.0")],
            [dict(equal="1.0"), True, dict(greater_equal="1.0", less_equal="2.0")],
            [dict(equal="1.0"), True, dict(greater="0.9", less="2.0")],
            [dict(equal="1.0"), True, dict(greater="0.9", less_equal="2.0")],
            [dict(greater_equal="1.0", less="2.0"), False, dict(equal="1.0")],
            [dict(greater_equal="1.0", less_equal="2.0"), False, dict(equal="1.0")],
            [dict(greater="0.9", less="2.0"), False, dict(equal="1.0")],
            [dict(greater="0.9", less_equal="2.0"), False, dict(equal="1.0")],
            [dict(equal="1.0"), False, dict(greater="1.0")],
            [dict(equal="1.0"), False, dict(less="1.0")],
            [dict(less="1.0"), True, dict(less="1.0")],
            [dict(less="0.9"), True, dict(less="1.0")],
            [dict(less="0.9"), True, dict(less_equal="1.0")],
            [dict(less_equal="0.9"), True, dict(less="1.0")],
            [dict(less_equal="0.9"), True, dict(less_equal="1.0")],
            [dict(less_equal="1.0"), False, dict(less="1.0")],
            [dict(less="1.0"), False, dict(less_equal="0.9")],
            [dict(greater_equal="1.0"), False, dict(greater="1.0")],
            [dict(greater="1.0"), False, dict(greater_equal="1.1")],
            [dict(), False, dict(less="1.0")],
            [dict(greater_equal="0.5", less_equal="1.0"), True, dict(less="2.0")],
            [dict(greater="0.5", less_equal="1.0"), True, dict(less="2.0")],
            [dict(greater="0.5", less="1.0"), True, dict(less="1.0")],
            [dict(less="1.0"), False, dict(greater="0.5", less="1.0")],
            [dict(less="1.0"), False, dict(greater="0.5", less_equal="1.0")],
            [dict(less="1.0"), False, dict(greater_equal="0.5", less="1.0")],
            [dict(less="1.0"), False, dict(greater_equal="0.5", less_equal="1.0")],
        ]

        for test, cmp, other in tests:
            t = conda_envfile.VersionRange(**test)
            o = conda_envfile.VersionRange(**other)

            if cmp:
                self.assertTrue(t in o)
            else:
                self.assertTrue(t not in o)


if __name__ == "__main__":

    unittest.main(verbosity=2)
