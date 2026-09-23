# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pilot',ROOT/'tools/dx500_pipeline.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PilotTests(unittest.TestCase):
    def setUp(self):self.s=p.load_spec()
    def invalid(self,change):
        change(self.s)
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'s.json';f.write_text(json.dumps(self.s))
            with self.assertRaises(ValueError):p.load_spec(f)
    def test_axis(self):self.assertEqual(p.xyz([-250,10,20]),(10,250,20))
    def test_design(self):
        parts,zones,c=p.design(self.s);self.assertEqual(p.design_check(parts,zones)['reserved_hull_intersections'],[])
        self.assertEqual(len({q['name'] for q in c}),len(c))
        self.assertEqual(sum(q['kind']=='engine_l' for q in c),4)
    def test_cavity_is_real(self):
        parts,zones,c=p.design(self.s)
        parts.append(p.primitive('bad_solid',(0,-27.5,0),(260,85,160)))
        with self.assertRaises(ValueError):p.design_check(parts,zones)
    def test_contact_not_overlap(self):self.assertFalse(p.overlap(p.bounds([0,0,0],[2,2,2]),p.bounds([2,0,0],[2,2,2])))
    def test_overlap(self):self.assertTrue(p.overlap(p.bounds([0,0,0],[2,2,2]),p.bounds([1,0,0],[2,2,2])))
    def test_unit(self):self.invalid(lambda s:s.update(units='cm'))
    def test_version(self):self.invalid(lambda s:s.update(schema_version=2))
    def test_nan(self):self.invalid(lambda s:s['modules'][0]['center'].__setitem__(0,float('nan')))
    def test_inf(self):self.invalid(lambda s:s['modules'][0]['size'].__setitem__(0,float('inf')))
    def test_zero(self):self.invalid(lambda s:s['modules'][0]['size'].__setitem__(0,0))
    def test_bool(self):self.invalid(lambda s:s['modules'][0]['center'].__setitem__(0,True))
    def test_name(self):self.invalid(lambda s:s['modules'][0].update(name='M02_command'))
    def test_engine_count(self):self.invalid(lambda s:s['engines'].pop())
    def test_bevel(self):self.invalid(lambda s:s['modules'][0].update(bevel=-1))

if __name__=='__main__':unittest.main()
