# SUMO / SigmaVM mapping materials

This directory is a historical archive of the SUMO (Suggested Upper Merged
Ontology) mapping environment used during earlier ontology work. It is not part
of the release pipeline: `scripts/ontology.py` does not read this directory, and
the public CI gate does not execute it.

## Files

- `READ_ME_SigmaVM.txt` — how to obtain the SigmaVM image and run the Sigma
  browser interface. The VM is Ubuntu 22.04 with Tomcat; the interface is served
  at `http://<host>:8080/sigma/login.html`. The image is available by request
  and is not committed here.
- `SigmaVM_Full_History.txt` — the shell history used to build the VM from a
  stock Ubuntu 22.04 image: WordNet, the SUMO sources, SigmaKEE, and Tomcat.
- `mapping-template.csv` — an empty template for recording ontology-term to
  SUMO-term mappings. Its columns are `term_id`, `term`, `sumo_id`,
  `sumo_label`, `mapping_relation`, `confidence`, `review_status`, `reviewer`,
  `review_date`, `evidence`, and `notes`.

The canonical ontology release is published from `ontology.source.json` and
documented in [`../docs/source-data-contract.md`](../docs/source-data-contract.md).
Keep these files as historical evidence: do not treat the empty template as a
current mapping and do not regenerate the VM history.
