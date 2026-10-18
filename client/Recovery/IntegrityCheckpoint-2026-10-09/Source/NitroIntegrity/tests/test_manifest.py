import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_manifest',ROOT/'tools/build_manifest.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def container(commands):
    code=b'\0'*4
    inner=b'Kamek\0\0\2'+struct.pack('>6I',0,len(code),0,0,0,0)+code+commands
    return struct.pack('>4I',len(inner),0,0,0)+inner

def command(kind,address,*args):
    return struct.pack('>'+('I'*(2+len(args))),(kind<<24)|0xfffffe,address,*args)

class ManifestTests(unittest.TestCase):
    def test_absolute_widths_and_conditional(self):
        data=container(command(34,0x80500003,1)+command(37,0x80500006,2,3)+command(65,0x80500008,0x100))
        writes,n=m.pul_writes(data)
        self.assertEqual(n,3)
        self.assertEqual([(w[0],w[1]) for w in writes],[(0x80500003,0x80500004),(0x80500006,0x80500008),(0x80500008,0x8050000c)])
    def test_relative_writes_are_not_absolute(self):
        data=container(struct.pack('>II',(32<<24)|0x100,0x60000000))
        self.assertEqual(m.pul_writes(data),([],1))
    def test_bad_containers_fail(self):
        cases=[b'',container(b'')[:-1],container(command(255,0x80500000,1)),container(command(35,0x80500000,1))]
        data=bytearray(container(b''));data[23]=3;cases.append(bytes(data))
        for data in cases:
            with self.assertRaises(ValueError):m.pul_writes(data)
    def test_inverse_ambiguous_mapping_is_not_guessed(self):
        mapping=m.inverse_usa_map('[E]\n80500000-8050000f: -0x10\n80600000-8060000f: -0x100010\n[J]\n')
        self.assertEqual(m.pal_candidates(0x804ffff0,mapping),[0x80500000,0x80600000])
        self.assertEqual(m.pal_candidates(0x80000000,mapping),[])
    def test_generated_manifest(self):
        report=json.loads((ROOT.parent/'PulsarEngine/Security/NitroIntegrity/manifest_review.json').read_text())
        self.assertEqual(report['pal_kamek_commands'],11067)
        self.assertEqual(len(report['checks']),23)
        self.assertEqual(len({c['address'] for c in report['checks']}),23)
        decisions={c['purpose']:c for c in report['decisions']}
        self.assertIn('owned by',decisions['hit_response_a']['status'])
        self.assertIn('relocation',decisions['standalone_item_cheat_helper']['status'])
        self.assertIn('unaligned',decisions['rapid_input_unverified_address']['status'])
        self.assertIn('not an executable',decisions['reverse_speed_parameter']['status'])
        self.assertIn('ManifestRuntimeReviewed = false', (ROOT.parent/'PulsarEngine/Security/NitroIntegrity/Manifest.hpp').read_text())

if __name__=='__main__':unittest.main()
