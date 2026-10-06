from pathlib import Path
import json, random
import pandas as pd
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from torchvision.models import resnet18, ResNet18_Weights

random.seed(7)
df=pd.read_csv('data/labels.csv')
df['path']=df['filename'].map(lambda x: Path('data')/x)
parts=[]
for (_, label), g in df.groupby(['slide_id','label']): parts.append(g.sample(min(10,len(g)), random_state=7))
s=pd.concat(parts).sample(frac=1, random_state=7)
if len(s)>240: s=pd.concat([s[s.label=='parasitized'].sample(120,random_state=7),s[s.label=='uninfected'].sample(120,random_state=7)]).sample(frac=1,random_state=7)
weights=ResNet18_Weights.DEFAULT
model=resnet18(weights=weights); model.fc=torch.nn.Identity(); model.eval()
transform=weights.transforms()
class C(Dataset):
 def __len__(self): return len(s)
 def __getitem__(self,i): return transform(Image.open(s.iloc[i].path).convert('RGB')), i
with torch.inference_mode():
 out=[]
 for x, idx in DataLoader(C(),batch_size=32): out.append(model(x))
X=torch.cat(out).numpy(); y=(s.label=='parasitized').astype(int).to_numpy()
slide_labels=s.groupby('slide_id').label.first()
train_slides, test_slides=train_test_split(slide_labels.index, test_size=0.30, random_state=7, stratify=slide_labels)
train_set=set(train_slides); test_set=set(test_slides)
train_idx=[i for i,slide in enumerate(s.slide_id) if slide in train_set]
test_idx=[i for i,slide in enumerate(s.slide_id) if slide in test_set]
head=LogisticRegression(max_iter=2000, random_state=7).fit(X[train_idx],y[train_idx])
probs=head.predict_proba(X[test_idx]); pred=head.predict(X[test_idx]); conf=probs.max(1)
records=[]
for j,i in enumerate(test_idx):
 r=s.iloc[i]
 records.append({'filename':r.filename,'slide_id':r.slide_id,'csv_label':r.label,'model_prediction':'parasitized' if pred[j] else 'uninfected','agree':bool(pred[j]==y[i]),'confidence':float(conf[j])})
Path('results').mkdir(exist_ok=True)
Path('results/toolkit_check.json').write_text(json.dumps({'method':'frozen ResNet18 ImageNet features + LogisticRegression head','sample_size':len(s),'train_size':len(train_idx),'held_out_size':len(test_idx),'held_out_only':True,'records':records},indent=2))
print('sample',len(s),'train',len(train_idx),'held_out',len(test_idx),'agreement',sum(x['agree'] for x in records)/len(records))
print('confusion matrix [[TN,FP],[FN,TP]]'); print(confusion_matrix(y[test_idx],pred,labels=[0,1]))
print('disagreements')
for x in records:
 if not x['agree']: print(x['csv_label'],x['model_prediction'],f"{x['confidence']:.3f}",x['filename'])
print('lowest confidence held-out')
for x in sorted(records,key=lambda z:z['confidence'])[:6]: print(x['csv_label'],x['model_prediction'],f"{x['confidence']:.3f}",x['filename'])
