from pathlib import Path
import csv
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
app = FastAPI(title="Patient-Slide Malaria Triage Review")

def slide_rows_with_samples():
    data = json.loads((RESULTS / "results.json").read_text())
    rows = data.get("slide_summary", [])
    by_slide = {r["slide_id"]: [] for r in rows}
    with (DATA / "labels.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r["slide_id"] in by_slide and len(by_slide[r["slide_id"]]) < 3:
                by_slide[r["slide_id"]].append({"filename": r["filename"], "label": r["label"]})
    for r in rows:
        r["sample_crops"] = by_slide[r["slide_id"]]
    return data

@app.get("/api/results")
def get_results():
    path = RESULTS / "results.json"
    if not path.exists():
        raise HTTPException(404, "results/results.json not found")
    return JSONResponse(slide_rows_with_samples())

@app.get("/images/{class_name}/{filename}")
def get_image(class_name: str, filename: str):
    if class_name not in {"parasitized", "uninfected"}:
        raise HTTPException(404)
    path = DATA / "images" / class_name / filename
    if not path.is_file() or path.parent.resolve() != (DATA / "images" / class_name).resolve():
        raise HTTPException(404)
    return FileResponse(path)

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><script src="https://cdn.tailwindcss.com"></script><title>Patient-slide malaria triage review</title></head><body class="bg-slate-100 text-slate-900"><main class="max-w-7xl mx-auto p-6"><h1 class="text-3xl font-bold">Patient-slide malaria triage review</h1><section id="summary" class="bg-white rounded-xl p-5 mt-5 shadow"></section><section id="slides" class="grid md:grid-cols-2 xl:grid-cols-3 gap-5 mt-6"></section></main><script>
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct=x=>x==null?'unknown':(Number(x)*100).toFixed(2)+'%';
fetch('/api/results').then(r=>r.json()).then(d=>{const rows=d.slide_summary||[];const shares=rows.filter(x=>x.infected_cell_share>0).map(x=>x.infected_cell_share);const free=rows.filter(x=>x.infected_cell_share===0);document.querySelector('#summary').innerHTML=`<div class="text-xl font-semibold">${rows.length} patient slides</div><p class="mt-2"><b>Infected-cell share:</b> ${shares.length?(Math.min(...shares)*100).toFixed(2)+'%–'+(Math.max(...shares)*100).toFixed(2)+'% across nonzero-share slides':'unknown'}; ${free.length} zero-share slides.</p><p class="mt-2 text-sm">Caveat: this is a screening share among photographed crops, not clinical parasitemia; staining and image quality vary between slides.</p>`;document.querySelector('#slides').innerHTML=rows.map(x=>{const review=x.decision==='REVIEW';const samples=(x.sample_crops||[]).map(s=>`<img class="h-24 w-24 object-contain bg-slate-900 rounded" src="/images/${encodeURIComponent(s.label)}/${encodeURIComponent(s.filename.split('/').pop())}" alt="${esc(s.label)} crop">`).join('');return `<article class="bg-white rounded-xl shadow overflow-hidden"><div class="p-5"><div class="flex justify-between gap-2 items-start"><h2 class="font-bold text-lg">${esc(x.slide_id)}</h2><span class="px-2 py-1 rounded text-xs font-bold ${review?'bg-red-100 text-red-800':'bg-green-100 text-green-800'}">${esc(x.decision)}</span></div><p class="text-sm text-slate-500 mt-1">Malaria status: ${esc(x.malaria_status)}</p><dl class="mt-4 text-sm space-y-1"><div class="flex justify-between"><dt>Total cells</dt><dd>${x.total_cell_count}</dd></div><div class="flex justify-between"><dt>Infected cells</dt><dd>${x.infected_cell_count}</dd></div><div class="flex justify-between"><dt>Clean cells</dt><dd>${x.clean_cell_count}</dd></div><div class="flex justify-between"><dt>Infected share</dt><dd>${pct(x.infected_cell_share)}</dd></div></dl><div class="flex flex-wrap gap-2 mt-4">${samples||'<span class="text-sm text-slate-500">No sample crops recorded</span>'}</div></div></article>`}).join('')}).catch(e=>document.querySelector('#summary').textContent='Could not load results/results.json: '+e);
</script></body></html>''')
