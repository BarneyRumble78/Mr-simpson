import sys, json; sys.path.insert(0,'.')
import narrate as n
from concurrent.futures import ThreadPoolExecutor
REF="2dcdbe54ea5546e1ad3b0be1600c4fe6"
segs=n.mark(n.parse())
jobs=[]
for i,sg in enumerate(segs):
    sg["chunks"]=n.split_sentences(sg["text"])
    for c in sg["chunks"]: jobs.append((sg["style"],c))
print(len(jobs),"chunks",flush=True)
done=0
def go(j):
    global done
    p=n.tts(j[1],j[0],REF); done+=1
    if done%20==0: print(done,"/",len(jobs),flush=True)
    return p
with ThreadPoolExecutor(4) as ex: paths=list(ex.map(go,jobs))
k=0
for sg in segs:
    sg["files"]=paths[k:k+len(sg["chunks"])]; k+=len(sg["chunks"])
json.dump(segs,open("segs.json","w"))
print("DONE",flush=True)
