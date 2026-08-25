import hashlib
import json


CONTRACT = "contracts/SupplyChainPoisonGate.py"
ZERO_HASH = "0" * 64
ONE_HASH = "1" * 64
TWO_HASH = "2" * 64
BOND = 1_000_000_000_000_000
DEPOSIT = 100_000_000_000_000


def deploy(direct_deploy, direct_vm, direct_owner):
    direct_vm.sender = direct_owner
    return direct_deploy(CONTRACT)


def enroll(contract, direct_vm, maintainer, value=BOND, deposit=DEPOSIT):
    direct_vm.sender = maintainer
    direct_vm.value = value
    result = contract.enroll_package("npm", "vault-kit", "https://github.com/example/vault-kit", ZERO_HASH, deposit)
    direct_vm.value = 0
    return result


def test_owner_host_registry_and_authorization(direct_deploy, direct_vm, direct_owner, direct_alice):
    contract = deploy(direct_deploy, direct_vm, direct_owner)
    direct_vm.sender = direct_alice
    assert contract.set_evidence_host("raw.githubusercontent.com", 1) == "OWNER_ONLY"
    direct_vm.sender = direct_owner
    assert contract.set_evidence_host("raw.githubusercontent.com", 1) == "HOST_REGISTERED"
    assert contract.set_evidence_host("raw.githubusercontent.com", 0) == "HOST_UPDATED"


def test_real_payable_bond_is_recorded(direct_deploy, direct_vm, direct_owner, direct_alice):
    contract = deploy(direct_deploy, direct_vm, direct_owner)
    assert enroll(contract, direct_vm, direct_alice) == 0
    package = json.loads(contract.get_package(0))
    totals = json.loads(contract.get_vault_totals())
    assert package["bond"] == BOND
    assert package["report_deposit"] == DEPOSIT
    assert package["state"] == "ACTIVE"
    assert totals == {"bonded": BOND, "report_deposits": 0, "slashed": 0}


def test_report_requires_exact_deposit_and_non_maintainer(direct_deploy, direct_vm, direct_owner, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm, direct_owner)
    enroll(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    direct_vm.value = DEPOSIT
    try:
        contract.open_report(0, "self", ZERO_HASH, ONE_HASH, TWO_HASH)
        assert False, "expected payable rollback"
    except Exception as exc:
        assert "MAINTAINER_CANNOT_SELF_REPORT" in str(exc)
    direct_vm.sender = direct_bob
    direct_vm.value = DEPOSIT - 1
    try:
        contract.open_report(0, "wrong", ZERO_HASH, ONE_HASH, TWO_HASH)
        assert False, "expected payable rollback"
    except Exception as exc:
        assert "WRONG_REPORT_DEPOSIT" in str(exc)
    direct_vm.value = DEPOSIT
    assert contract.open_report(0, "report-1", ZERO_HASH, ONE_HASH, TWO_HASH) == 0
    direct_vm.value = 0
    report = json.loads(contract.get_report(0))
    assert report["state"] == "COLLECTING"
    assert report["deposit"] == DEPOSIT
    assert json.loads(contract.get_vault_totals())["report_deposits"] == DEPOSIT


def test_evidence_roles_host_and_seal_guards(direct_deploy, direct_vm, direct_owner, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm, direct_owner)
    direct_vm.sender = direct_owner
    assert contract.set_evidence_host("raw.githubusercontent.com", 1) == "HOST_REGISTERED"
    enroll(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    direct_vm.value = DEPOSIT
    assert contract.open_report(0, "report-1", ZERO_HASH, ONE_HASH, TWO_HASH) == 0
    direct_vm.value = 0
    url = "https://raw.githubusercontent.com/org/repo/main/evidence.json"
    assert contract.attach_evidence(0, "UNKNOWN", url, ZERO_HASH) == "INVALID_EVIDENCE_KIND"
    assert contract.attach_evidence(0, "DIFF", "https://evil.example/a", ZERO_HASH) == "HOST_NOT_ALLOWED"
    assert contract.attach_evidence(0, "DIFF", url, ZERO_HASH) == 0
    assert contract.attach_evidence(0, "DIFF", url + "?two", ZERO_HASH) == "EVIDENCE_KIND_ALREADY_ATTACHED"
    assert contract.seal_report(0, ZERO_HASH) == "INCOMPLETE_EVIDENCE_SET"
    assert contract.attach_evidence(0, "CHANGELOG", url + "?changelog", ONE_HASH) == 1
    assert contract.attach_evidence(0, "TREE", url + "?tree", TWO_HASH) == 2
    assert contract.seal_report(0, "f" * 64) == "MANIFEST_MISMATCH"
    manifest = {"base_commit": ZERO_HASH, "evidence": [{"kind": "DIFF", "sha256": ZERO_HASH, "url": url}, {"kind": "CHANGELOG", "sha256": ONE_HASH, "url": url + "?changelog"}, {"kind": "TREE", "sha256": TWO_HASH, "url": url + "?tree"}], "report_key": "report-1", "target_commit": ONE_HASH, "target_tree_sha256": TWO_HASH}
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    assert contract.seal_report(0, hashlib.sha256(canonical.encode()).hexdigest()) == "REPORT_SEALED"
    assert json.loads(contract.get_report(0))["state"] == "SEALED"


def test_withdraw_blocked_while_report_open(direct_deploy, direct_vm, direct_owner, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm, direct_owner)
    enroll(contract, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    direct_vm.value = DEPOSIT
    assert contract.open_report(0, "report-1", ZERO_HASH, ONE_HASH, TWO_HASH) == 0
    direct_vm.value = 0
    direct_vm.sender = direct_alice
    assert contract.withdraw_bond(0) == "REPORT_STILL_OPEN"
    assert json.loads(contract.get_package(0))["bond"] == BOND
