from cubicweb.devtools.testlib import CubicWebTC


class LocalpermsTC(CubicWebTC):

    def test_dummy(self):
        # Just ensure the test database is created without errors
        pass


if __name__ == "__main__":
    import unittest

    unittest.main()
