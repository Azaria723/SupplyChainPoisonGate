"""Run a real Studionet lifecycle. Keys are read only from process environment."""

import hashlib
import json
import os
import urllib.request

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus


ADDRESS = "0x667126d44229a85cc635D35df74C990fF403D15d"
BOND = 1_000_000_000_000_000
DEPOSIT = 100_000_000_000_000
BASE = hashlib.sha256(b"genlayer-js:baseline:1b7f50a3a3f2963ea857941b0fb386081dd5c326").hexdigest()
TARGET = hashlib.sha256(b"genlayer-js:target:1b7f50a3a3f2963ea857941b0fb386081dd5c326").hexdigest()
URLS = (
    ("DIFF", "https://raw.githubusercontent.com/genlayerlabs/genlayer-js/1b7f50a3a3f2963ea857941b0fb386081dd5c326/README.md"),
    ("CHANGELOG", "https://raw.githubusercontent.com/genlayerlabs/genlayer-cli/3396474b775d998ab3778ac7cfd1e2e197f8b47f/CHANGELOG.md"),
    ("TREE", "https://raw.githubusercontent.com/genlayerlabs/genlayer-js/1b7f50a3a3f2963ea857941b0fb386081dd5c326/package.json"),
)


def accepted(client, tx_hash, label):
    print(f"TX {label}: {tx_hash.hex() if hasattr(tx_hash, 'hex') else tx_hash}", flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx_hash, status=TransactionStatus.ACCEPTED, interval=2000, retries=90
    )
    print(f"ACCEPTED {label}: {receipt}", flush=True)
    return receipt


def main():
    maintainer = create_account(os.environ["SUPPLYCHAIN_MAINTAINER_KEY"])
    hunter = create_account(os.environ["SUPPLYCHAIN_HUNTER_KEY"])
    client = create_client(studionet, account=maintainer)
    print(f"MAINTAINER {maintainer.address}", flush=True)
    print(f"HUNTER {hunter.address}", flush=True)
    print(f"BALANCE maintainer={client.get_balance(maintainer.address)} hunter={client.get_balance(hunter.address)}", flush=True)
    print("BEFORE", client.read_contract(ADDRESS, "get_vault_totals"), flush=True)

    packets = []
    for kind, url in URLS:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read()
        packets.append({"kind": kind, "url": url, "sha256": hashlib.sha256(body).hexdigest()})
    tree_digest = hashlib.sha256(json.dumps(packets, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    report_key = "studionet-benign-20260825-01"

    tx = client.write_contract(
        ADDRESS,
        "enroll_package",
        account=maintainer,
        value=BOND,
        args=["npm", "genlayer-js-lifecycle-20260825-01", "https://github.com/genlayerlabs/genlayer-js", BASE, DEPOSIT],
    )
    accepted(client, tx, "enroll_package")
    print("PACKAGE", client.read_contract(ADDRESS, "get_package", args=[0]), flush=True)

    tx = client.write_contract(
        ADDRESS,
        "open_report",
        account=hunter,
        value=DEPOSIT,
        args=[0, report_key, BASE, TARGET, tree_digest],
    )
    accepted(client, tx, "open_report")

    for packet in packets:
        tx = client.write_contract(
            ADDRESS,
            "attach_evidence",
            account=hunter,
            args=[0, packet["kind"], packet["url"], packet["sha256"]],
        )
        accepted(client, tx, "attach_" + packet["kind"].lower())

    manifest = {
        "base_commit": BASE,
        "evidence": packets,
        "report_key": report_key,
        "target_commit": TARGET,
        "target_tree_sha256": tree_digest,
    }
    manifest_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print("MANIFEST", manifest_hash, flush=True)
    tx = client.write_contract(ADDRESS, "seal_report", account=hunter, args=[0, manifest_hash])
    accepted(client, tx, "seal_report")
    print("SEALED", client.read_contract(ADDRESS, "get_report", args=[0]), flush=True)

    tx = client.write_contract(ADDRESS, "adjudicate", account=hunter, args=[0])
    accepted(client, tx, "adjudicate")
    print("FINAL_PACKAGE", client.read_contract(ADDRESS, "get_package", args=[0]), flush=True)
    print("FINAL_REPORT", client.read_contract(ADDRESS, "get_report", args=[0]), flush=True)
    print("FINAL_TOTALS", client.read_contract(ADDRESS, "get_vault_totals"), flush=True)


if __name__ == "__main__":
    main()
