# docs/_generated — generated documents

Every file in this directory is written by a script and must not be hand-edited. The
producer is named at the top of each file, and the `docs` gate arm
(`./run.sh docs`) fails when a generated document no longer matches the repository it
describes.

| File | Producer | Refresh with |
| --- | --- | --- |
| [`gate.md`](gate.md) | [`scripts/report_gate.py`](../../scripts/report_gate.py) | `./run.sh bench` |

Measured numbers (arm wall time, regression-test count, source term count) live here so
prose pages can link to them instead of copying literals. Prose may quote a number only
when it also names this directory as its source.
