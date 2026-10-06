## GOAL
Determine whether patient slides can be safely triaged for microscopist review using the infected-cell share among all photographed cells, while protecting slides containing convincing faint rings.

Operate with `uv`: create the environment with `uv venv` and run every Python command with `uv run` (the same workflow on every OS). Data is in `data/`: load the cell images from `data/images/` and their labels/slide tags from `data/labels.csv`; write outputs only to `results/`. Every number reported must be checked against the ground truth in the supplied files and transcript.

## MUST-NOT
- MUST NOT pool all cell crops; keep the patient slide as the unit and count every cell on each slide.
- MUST NOT call the infected-cell share among photographed crops clinical parasitemia.
- MUST NOT dismiss a slide containing one or two convincing faint rings because its share is small; it must be sent for human review.
- MUST NOT treat purple colour alone as infection: stain clumps, dust, debris, and platelets can imitate parasites.
- MUST NOT silently remove blurred, clipped, poorly lit, heavily or lightly stained, neighbouring, or otherwise doubtful crops from a slide's total, or change infection labels based on separate quality notes.
- MUST NOT invent missing file metadata, microscope details, slide-status mappings, or label provenance.

See `spec.md` for the complete problem specification.
