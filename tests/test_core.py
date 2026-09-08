import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from opus_eval_fabric.contextual import contextual_variants
from opus_eval_fabric.evaluator import evaluate
from opus_eval_fabric.io import mission_from_dict
from opus_eval_fabric.roundtrip import roundtrip_delta

class CoreTests(unittest.TestCase):
    def base(self):
        return {"mission":"test","evidence":{"source":"fixture","provenance":"local","uncertainty":"LOW"},"model":{"claim":"candidate","model_class":"working_model"},"action":{"action":"read","authority":"read-only","side_effect":"none"},"metadata":{"retorsion_edges":[]}}
    def test_valid_read_only_passes(self): self.assertEqual(evaluate(mission_from_dict(self.base())).verdict.value,"PASS")
    def test_forbidden_retorsion_blocks(self):
        d=self.base(); d["metadata"]["retorsion_edges"]=["MODEL->FACT"]; self.assertEqual(evaluate(mission_from_dict(d)).verdict.value,"BLOCK")
    def test_effectful_without_authority_blocks(self):
        d=self.base(); d["action"]={"action":"write","authority":"none","side_effect":"write"}; self.assertEqual(evaluate(mission_from_dict(d)).verdict.value,"BLOCK")
    def test_effectful_without_rollback_repairs(self):
        d=self.base(); d["action"]={"action":"write","authority":"approved","side_effect":"write","readback":"re-read"}; self.assertEqual(evaluate(mission_from_dict(d)).verdict.value,"REPAIR")
    def test_unknown_is_not_pass(self):
        d=self.base(); d["evidence"]["uncertainty"]="UNKNOWN"; self.assertEqual(evaluate(mission_from_dict(d)).verdict.value,"UNKNOWN")
    def test_context_variants(self): self.assertGreaterEqual(len(contextual_variants("a   b")),4)
    def test_roundtrip(self): self.assertTrue(roundtrip_delta({"b":2,"a":1},{"a":1,"b":2})["lossless"])

class RegistryTests(unittest.TestCase):
    def test_code24(self):
        data=json.loads((ROOT/'src/opus_eval_fabric/code24.json').read_text(encoding='utf-8')); x=data['languages']; self.assertEqual(len(x),24); self.assertEqual(len({i['language'] for i in x}),24); self.assertEqual(len({i['upstream'] for i in x}),24)
    def test_transformers8(self):
        data=json.loads((ROOT/'configs/transformers8.json').read_text(encoding='utf-8')); self.assertEqual({x['id'] for x in data['operators']},{f'T{i}' for i in range(8)})
if __name__=='__main__': unittest.main()
