from pathlib import Path
import csv, json, shutil
from collections import defaultdict

rows = defaultdict(list)
with open('data/labels.csv', newline='') as f:
    for r in csv.DictReader(f):
        rows[r['slide_id']].append(r)

out = Path('results'); (out/'samples').mkdir(parents=True, exist_ok=True)
summary=[]
for slide, rs in rows.items():
    infected=sum(r['label']=='parasitized' for r in rs)
    total=len(rs)
    summary.append({'slide_id':slide,'total_cell_count':total,'infected_count':infected,
                    'clean_count':total-infected,'infected_cell_share':infected/total,
                    'decision':'REVIEW' if infected else 'SAFE'})
summary.sort(key=lambda x:x['total_cell_count'])
chosen=[]
for x in summary[:1]+summary[-1:]: chosen.append(x['slide_id'])
chosen.append(next(x['slide_id'] for x in summary if x['infected_count']==0))
for slide in dict.fromkeys(chosen):
    rs=rows[slide]
    for r in rs[:2]:
        src=Path('data')/r['filename']
        dst=out/'samples'/f"{slide}_{r['label']}_{src.name}"
        shutil.copy2(src,dst)
    for r in rs:
        if r['label']=='parasitized':
            src=Path('data')/r['filename']; dst=out/'samples'/f"{slide}_{r['label']}_{src.name}"
            shutil.copy2(src,dst); break
selected=[x for x in summary if x['slide_id'] in chosen]
result={'validation_slides':selected,'all_slide_summary':summary,
        'reconciles':sum(x['infected_count'] for x in summary)==956 and sum(x['clean_count'] for x in summary)==1431}
(out/'results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(selected,indent=2)); print('infected',sum(x['infected_count'] for x in summary),'clean',sum(x['clean_count'] for x in summary),'reconciles',result['reconciles'])
