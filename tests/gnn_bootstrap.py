"""GNN-arm integration test: run only after the pinned parser is installed.

The ordinary unit suite needs no parser; the GNN arm explicitly runs this module
rather than discovering it before provisioning its environment.
"""

from __future__ import annotations

import unittest

from gnn.importers import read_pin

from scripts.validate_gnn_conformance import PIN_PATH, bootstrap_pin


class BootstrapConsistencyTests(unittest.TestCase):
    def test_bootstrap_pair_matches_shipped_reader(self) -> None:
        bootstrap = bootstrap_pin(PIN_PATH)
        pin = read_pin(PIN_PATH)
        normalized = (pin.repository, pin.commit)
        self.assertEqual(bootstrap, normalized)
        print(f"bootstrap pair: {bootstrap!r}; read_pin pair: {normalized!r}")


if __name__ == "__main__":
    unittest.main()
