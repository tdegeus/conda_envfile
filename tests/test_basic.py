import unittest

import conda_envfile


class Test(unittest.TestCase):
    """ """

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
            self.assertEqual(str(conda_envfile.Specifier(name)), name)

        self.assertEqual(
            str(conda_envfile.Specifier("foo >=1.2.0, <=1.2.0")),
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
                conda_envfile.Specifier(dep)

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

        for deps, expected in dependencies:
            for _ in range(len(deps)):
                deps.append(deps.pop(0))
                self.assertEqual(conda_envfile.unique(*deps), expected)

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

    def test_remove(self):

        self.assertEqual(conda_envfile.remove(["foo", "bar"], "bar"), ["foo"])
        self.assertEqual(conda_envfile.remove(["foo *", "bar *"], "bar"), ["foo *"])
        self.assertEqual(conda_envfile.remove(["foo =1.*", "bar =1.*"], "bar"), ["foo =1.*"])
        self.assertEqual(conda_envfile.remove(["foo >1.0", "bar >1.0"], "bar"), ["foo >1.0"])

    def test_restrict(self):

        self.assertEqual(conda_envfile.restrict(["foo", "bar"], ["foo >1.0"]), ["foo >1.0", "bar"])


if __name__ == "__main__":

    unittest.main(verbosity=2)
