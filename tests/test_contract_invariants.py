import ast
from pathlib import Path


PATH = Path(__file__).parents[1] / "contracts" / "SupplyChainPoisonGate.py"
SOURCE = PATH.read_text(encoding="ascii")
TREE = ast.parse(SOURCE)
CLASS = next(node for node in TREE.body if isinstance(node, ast.ClassDef))


def method(name):
    return next(node for node in CLASS.body if isinstance(node, ast.FunctionDef) and node.name == name)


def segment(name):
    return ast.get_source_segment(SOURCE, method(name))


def test_exact_runner_header_and_name():
    lines = SOURCE.splitlines()
    assert lines[0] == "# v0.2.16"
    assert "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" in lines[1]
    assert CLASS.name == PATH.stem


def test_public_signatures_are_bounded():
    for node in CLASS.body:
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            assert len(node.args.args) - 1 <= 6, node.name


def test_custody_is_real_not_ledger_only():
    assert "@gl.public.write.payable" in SOURCE
    assert "gl.message.value" in SOURCE
    assert "emit_transfer" in segment("adjudicate")
    assert "emit_transfer" in segment("withdraw_bond")
    assert "user_error_immediate" in segment("enroll_package")
    assert "user_error_immediate" in segment("open_report")


def test_ai_result_is_closed_and_cross_field_validated():
    code = segment("adjudicate")
    assert "POISONED|NOT_PROVEN" in code
    assert "behavior_mask" in code
    assert "intent" in code
    assert "confidence" in code
    assert 'intent != "MALICIOUS"' in code
    assert 'confidence != "HIGH"' in code


def test_evidence_commitments_and_roles_are_mandatory():
    code = segment("attach_evidence") + segment("adjudicate")
    for role in ("DIFF", "CHANGELOG", "TREE"):
        assert role in code
    assert "hashlib.sha256(response.body)" in code
    assert "commitment_valid" in code
    assert "HOST_NOT_ALLOWED" in code


def test_manifest_is_recomputed_before_sealing():
    code = segment("seal_report")
    assert "json.dumps" in code
    assert "hashlib.sha256" in code
    assert "MANIFEST_MISMATCH" in code
