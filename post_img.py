import json,subprocess,time,sys
H='custom-cred:aebd08e0-a336-4f31-b710-e642c2630ec2@graph.instagram.com'; IG='17841421327198362'; B='https://graph.instagram.com/v23.0'
def call(args):
    r=subprocess.run(['pplx','credentials','run',H,'--','curl','-s']+args,capture_output=True,text=True); return json.loads(r.stdout or '{}')
def post_image(url,cap):
    c=call(['-X','POST',f'{B}/{IG}/media','--data-urlencode',f'image_url={url}','--data-urlencode',f'caption={cap}'])
    if 'id' not in c: return c
    for _ in range(20):
        s=call([f'{B}/{c["id"]}?fields=status_code'])
        if s.get('status_code') in ('FINISHED','ERROR'): break
        time.sleep(3)
    p=call(['-X','POST',f'{B}/{IG}/media_publish','--data-urlencode',f'creation_id={c["id"]}'])
    return p
if __name__=='__main__':
    q=json.load(open('wall_queue.json')); res=[]
    for o in q:
        r=post_image(o['url'],o['caption']); print(o['tag'],r,flush=True); res.append((o['tag'],r)); time.sleep(4)
    json.dump(res,open('wall_results.json','w'))
