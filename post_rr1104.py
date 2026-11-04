import json, subprocess, time, sys
H='custom-cred:aebd08e0-a336-4f31-b710-e642c2630ec2@graph.instagram.com'
IG='17841421327198362'; B='https://graph.instagram.com/v23.0'
SHA=sys.argv[1]; WHAT=sys.argv[2]
RAW=f'https://raw.githubusercontent.com/mikeizquierdo/ripmatic-ig-media/{SHA}/rr1104/'
CAP=open('/home/user/workspace/ig/rr1104/caption.txt').read().strip()
REEL_CAP="Who you gonna get? 🎲\n\nRandom Rush Wednesday: 10 MEGA boxes of 2026 Topps Neon Marvel, 218 random spots at $8. Whatnot's randomizer assigns your character on camera and the hits of your character are yours. 10 numbered parallels guaranteed on the board.\n\nLive Wednesday 4 PM PT on Whatnot @ripmatics. We rip as soon as the board fills.\n\n#ToppsNeon #NeonMarvel #MarvelCards #Whatnot #CardBreaks #RandomBreak #Ripmatic"
def call(a):
    r=subprocess.run(['pplx','credentials','run',H,'--','curl','-s']+a,capture_output=True,text=True)
    try: return json.loads(r.stdout or '{}')
    except Exception: return {'raw':r.stdout[:300]}
def create(p):
    a=['-X','POST',f'{B}/{IG}/media']
    for k,v in p.items(): a+=['--data-urlencode',f'{k}={v}']
    return call(a)
def wait(cid,tries=60,d=5):
    s={}
    for _ in range(tries):
        s=call([f'{B}/{cid}?fields=status_code,status'])
        if s.get('status_code') in('FINISHED','ERROR','EXPIRED'):break
        time.sleep(d)
    return s
def pub(cid):
    p=call(['-X','POST',f'{B}/{IG}/media_publish','--data-urlencode',f'creation_id={cid}'])
    if 'id' in p: p.update(call([f"{B}/{p['id']}?fields=permalink,media_type,timestamp"]))
    return p
out={}
if WHAT=='carousel':
    kids=[create({'image_url':RAW+f,'is_carousel_item':'true'}).get('id') for f in ['feed_1.jpg','feed_2.jpg','feed_3.jpg']]
    out['kids']=kids
    c=create({'media_type':'CAROUSEL','children':','.join(kids),'caption':CAP}); out['c']=c
    if wait(c['id']).get('status_code')=='FINISHED': out['pub']=pub(c['id'])
elif WHAT in('story_tomorrow','story_today'):
    c=create({'media_type':'STORIES','image_url':RAW+WHAT+'.jpg'}); out['c']=c
    if wait(c['id']).get('status_code')=='FINISHED': out['pub']=pub(c['id'])
elif WHAT=='reel':
    c=create({'media_type':'REELS','video_url':RAW+'reel.mp4','cover_url':RAW+'cover.jpg','caption':REEL_CAP,'share_to_feed':'true'}); out['c']=c
    s=wait(c['id'],tries=90); out['s']=s
    if s.get('status_code')=='FINISHED': out['pub']=pub(c['id'])
print(json.dumps(out))
