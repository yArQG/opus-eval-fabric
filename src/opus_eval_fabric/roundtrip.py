from __future__ import annotations
import json

def canonical_json(value) -> str:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def roundtrip_delta(original, rebuilt) -> dict:
    a,b=canonical_json(original),canonical_json(rebuilt)
    return {"lossless": a==b, "original":a, "rebuilt":b}
