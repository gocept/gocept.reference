import gocept.reference.fix
import gocept.reference.reference
import gocept.reference.testing as grt
import pytest
import zope.component.hooks

try:
    import unittest.mock as mock  # PY2
except ImportError:
    import mock


class TestFixer(grt.TestCase):
    """Testing .fix.Fixer"""

    def setUp(self):
        super(TestFixer, self).setUp()
        root = self.getRootFolder()
        zope.component.hooks.setSite(root)

        root['jena'] = jena = grt.City()
        root['rosenkeller'] = rosenkeller = grt.CulturalInstitution()
        jena.cultural_institutions = set((rosenkeller,))

        root['cospeda'] = cospeda = grt.Village()
        root['museum_1806'] = museum_1806 = grt.CulturalInstitution()
        cospeda.cultural_institutions = set((museum_1806,))

        root['thomas'] = thomas = grt.Address()
        thomas.city = jena

        hanfried = grt.Monument()
        hanfried.city = jena
        root['hanfried'] = hanfried

    @pytest.fixture(scope='function', autouse=True)
    def store_capsys(self, capsys):
        self.capsys = capsys

    def test_fix__Fixer__fix_reference_counts__1(self):
        """It commits savepoints if specified."""
        fixer = gocept.reference.fix.Fixer()
        with mock.patch('transaction.savepoint') as sp:
            fixer.fix_reference_counts()
        assert sp.call_count == 0

        fixer = gocept.reference.fix.Fixer(
            do_savepoints=True, savepoint_step=2)

        with mock.patch('transaction.savepoint') as sp:
            fixer.fix_reference_counts()
        assert sp.call_count == 14

    def test_fix__Fixer__fix_reference_counts__2(self):
        """It logs progress if specified."""
        fixer = gocept.reference.fix.Fixer()
        fixer.fix_reference_counts()

        captured = self.capsys.readouterr()
        assert captured.out == ""

        fixer = gocept.reference.fix.Fixer(
            do_savepoints=False, savepoint_step=7, verbose=True)

        fixer.fix_reference_counts()

        captured = self.capsys.readouterr()
        assert captured.out == ("""\
7 objects reseted.
14 objects reseted.
7 objects registered.
14 objects registered.
""")
