# Summary

## Goal
Determine whether a patient's malaria slide can be safely triaged for microscopist review
using the infected-cell share among all its photographed cells, without dismissing slides
containing convincing faint rings.

## Result vs. baseline
All 2,387 crops were reconciled to the verified ground-truth totals (956 infected / 1,431
clean) across 24 patient slides. Each slide is reported with its total, infected, and clean
cell counts and its infected-cell share: 0% for 8 slides, 14.63%-90.00% for the other 16. No
malaria-status (positive/free) field could be recovered from the supplied files, so slides
are reported by share only, not compared against a confirmed 16-vs-8 split.

As an independent check on label quality, a frozen ImageNet-pretrained ResNet18 feature
extractor plus a logistic-regression head, evaluated on a genuinely held-out, slide-grouped
77-crop split (never seen while fitting the head), agreed with the existing infected/clean
labels 90.91% of the time — against a 53.25% majority-class baseline computed on the same
held-out set. That is roughly a 38-point improvement over the trivial baseline.

## Imaging caveat
Giemsa staining strength and image quality vary between slides. A frozen ImageNet feature
extractor may rely partly on stain intensity/contrast rather than true parasite morphology:
heavy staining could make purple marks easier to flag (inflating agreement) or cause stain
clumps to be mistaken for parasites (deflating agreement); pale or unevenly lit slides could
hide faint rings. So the 90.91% figure describes this specific held-out mix of slides, not a
validated general accuracy. Separately, the proposed review cutoff (infected-cell share >=
14.63%) is mathematically identical to a plain "zero vs nonzero infected cells" rule — it
equals the smallest nonzero share observed in this 24-slide sample and carries no safety
margin against a genuinely low-share slide; the explicit "any convincing faint ring goes to
review" override, not the numeric cutoff, is what is meant to catch that case.

## AI-use disclosure
An AI coding agent ("Pi") was directed throughout to inspect the actual data files (not
just the interview transcript) before making any claim, and to check every number against
file-derived ground truth. A second AI (Claude, used as a reviewing collaborator) cross-
checked Pi's outputs against the interview transcript, spec.md, and AGENTS.md at every step,
and verified the arithmetic reported above by hand.

Pi's outputs were not accepted at face value. Two mismatched, unadapted course-template
prompts were caught before being run to completion or accepted: one asked for a
nuclei-counting/Cellpose analysis against ground-truth masks that do not exist in this
dataset (Pi itself correctly refused rather than fabricate a result); a later one produced a
"field/overlay" results app built for the wrong scenario, which had to be identified and
rebuilt around the actual 24-slide data. A first classification sanity-check reporting 100%
agreement was rejected because it evaluated the model on its own training data, and was
redone with a genuine held-out, slide-grouped split, which produced the 90.91%/53.25%
figures above. The malaria-status mapping was deliberately left "unknown" throughout rather
than inferred from the coincidental match between the 8 zero-infected-cell slides and the
stated count of 8 malaria-free patients, since no file confirmed that mapping. The proposed
numeric review cutoff was explicitly labeled as equivalent to a trivial split with no safety
margin, rather than presented as a validated threshold.
