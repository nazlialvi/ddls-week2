# Specification

## Decision
The owner needs to decide whether a patient slide can be safely triaged from the infected-cell share among all its photographed cells, so obvious clean slides may be set aside and suspicious slides sent to a microscopist. The final unit is the slide, not the individual cell or a pooled collection; any slide with even one or two convincing faint rings must go to human review.

## Task
This is **cell-level binary classification followed by slide-level counting/aggregation**, not segmentation or object detection. For every crop, retain the supplied `parasitized`/`uninfected` label; for each slide, count all cells and infected cells and calculate `infected_count / total_cell_count`. The output is a slide-level screening rule, not clinical parasitemia.

## Data
- Manifest and labels: `data/labels.csv`, with columns `filename`, `label`, and `slide_id`.
- Images: `data/images/parasitized/` and `data/images/uninfected/` (PNG files). The CSV paths use `images/parasitized/` and `images/uninfected/`; resolve them to the supplied `data/images/` directories.
- The transcript describes 2,387 one-red-cell crops from Giemsa-stained thin blood films, ordinary colour bright-field microscope photographs, from 24 patient slides: 16 malaria-positive and 8 malaria-free. It reports 956 infected and 1,431 clean cells. These totals must be verified against the files.
- Pixel dimensions are not uniform: inspecting all 2,387 PNG headers gives 665 distinct `(width, height)` pairs, ranging from 49 x 58 to 259 x 235 pixels. All 2,387 files are verified as 8-bit RGB PNGs (`file` reports `8-bit/color RGB`; PNG color type 2), so each image has three 8-bit colour channels (red, green, blue) and no alpha channel. Magnification, pixel size, microscope/camera details, and file-size/acquisition metadata are unknown from the supplied record unless the files establish them. The transcript identifies the modality as ordinary bright-field colour microscopy, not confocal, and the stain as Giemsa.
- The target is an intracellular malaria parasite, usually a deep-purple chromatin dot with a paler bluish ring; larger forms may occur. Clean cells are pinkish-grey discs. The supplied cell labels are encoded in the CSV as `parasitized` or `uninfected`; no pixel-level parasite masks/outlines are supplied.
- Slide malaria-status mapping is not stated in the CSV excerpt/record as a separate field. Recover it only from supplied files/records if present; otherwise mark it unknown rather than inventing it.

## Done
Done means all supplied crops are accounted for and assigned to a slide; every slide has total, infected, clean, share, and status where supported; counts reconcile to the verified file totals; the 16 malaria-positive and 8 malaria-free slides are compared separately if the mapping is available; and quality concerns are reported separately. The result must show the 24 slide rows, including the number of crops with quality concerns and the number of doubtful readings sent for human review, plus smallest/largest slide totals and shares only after computing and checking them, and a plain review rule with an explicit faint-ring override. Poor-quality crops must not be silently removed from totals or have their infection labels changed.

## Metric and baseline
Primary metric: **slide-level infected-cell share**, `infected cells / all photographed cells`, with one value per slide. The baseline to beat is the owner’s required reference calculation: use every cell, preserve slide tags, count supplied infected/clean labels, and do not pool all 2,387 cells. For the screening decision, compare the slide-level shares of malaria-positive versus malaria-free slides and report the rule’s handling of faint rings; no numerical cut-off is specified by the transcript before the 24 verified rows and status mapping are recovered.

## Traps
- Do not pool cells across slides or report the share as clinical parasitemia.
- Do not omit clean cells, poor-quality crops, or malaria-free slides.
- Purple stain clumps, dust, debris, and platelets can mimic parasites; purple colour alone is insufficient.
- Faint early rings can be genuine and must not be dismissed because the share is small; a convincing one should trigger review.
- Watch blur/out-of-focus crops, uneven illumination or glare, heavy/pale staining, clipped cell edges, black corners, and neighbouring cells.
- Keep blur, clipping, lighting, stain, neighbour, artifact, and confidence observations separate from the original infection label; these QC annotations are not defined in the supplied data and must not be invented as existing labels.
- Check duplicate, missing, unreadable, excluded, or corrected files, label provenance/review criteria, and slide/patient linkage before making claims. Do not claim independent confirmation or clinical representativeness without records.
- Check every reported number against the CSV/image files and the transcript ground truth.
