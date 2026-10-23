import json, subprocess, time, sys
H = 'custom-cred:aebd08e0-a336-4f31-b710-e642c2630ec2@graph.instagram.com'
IG = '17841421327198362'; B = 'https://graph.instagram.com/v23.0'
SHA = sys.argv[1]; WHAT = sys.argv[2]
RAW = f'https://raw.githubusercontent.com/mikeizquierdo/ripmatic-ig-media/{SHA}/neon1023/'

def call(args):
    r = subprocess.run(['pplx', 'credentials', 'run', H, '--', 'curl', '-s'] + args, capture_output=True, text=True)
    try: return json.loads(r.stdout or '{}')
    except Exception: return {'raw': r.stdout[:300]}

def create(params):
    a = ['-X', 'POST', f'{B}/{IG}/media']
    for k, v in params.items(): a += ['--data-urlencode', f'{k}={v}']
    return call(a)

def wait(cid, tries=60, delay=5):
    s = {}
    for _ in range(tries):
        s = call([f'{B}/{cid}?fields=status_code,status'])
        if s.get('status_code') in ('FINISHED', 'ERROR', 'EXPIRED'): break
        time.sleep(delay)
    return s

def publish(cid):
    return call(['-X', 'POST', f'{B}/{IG}/media_publish', '--data-urlencode', f'creation_id={cid}'])

def link(mid):
    return call([f'{B}/{mid}?fields=permalink,media_type,timestamp'])

REEL_CAP = """4 hobby boxes. 156 spots. One break.

Tomorrow (Fri) 4 PM PT we rip 2026 Topps Neon Marvel live on Whatnot. Pick your character, spots from $10, and every card of your character is yours: base, parallels, numbered, autos, sketches.

Chase numbered parallels, Chrome Neon Etch, autos and sketches. The Wildcard spot takes everything not on the board.

Set a reminder: whatnot.com/user/ripmatics (link in bio) @ripmatics

#marvelcards #toppsneon #toppsmarvel #neonmarvel #cardbreaks #whatnot #pickyourcharacter #marvelcollector #spiderman #venom #wolverine"""

CAR_CAP = """Who are you ripping for?

Friday 4 PM PT: four sealed hobby boxes of 2026 Topps Neon Marvel, 156 character spots starting at $10. Every card of your character is yours.

Swipe for the chase cards and the Wildcard spot that gets every card not on the board.

Set a reminder: whatnot.com/user/ripmatics (link in bio) @ripmatics

#marvelcards #toppsneon #neonmarvel #cardbreaks #whatnot #marvelcollector"""

out = {}
if WHAT == 'reel':
    c = create({'media_type': 'REELS', 'video_url': RAW + 'reel.mp4', 'caption': REEL_CAP, 'share_to_feed': 'true'})
    out['create'] = c
    if 'id' in c:
        out['status'] = wait(c['id'])
        if out['status'].get('status_code') == 'FINISHED':
            p = publish(c['id']); out['publish'] = p
            if 'id' in p: out['link'] = link(p['id'])
elif WHAT == 'carousel':
    kids = []
    for f in ['1-neon-break.jpg', '2-chase-the-hits.jpg', '3-wildcard.jpg', '4-pick-your-character.jpg']:
        k = create({'image_url': RAW + f, 'is_carousel_item': 'true'})
        if 'id' not in k: out['child_err'] = k; break
        wait(k['id'], 20, 3); kids.append(k['id'])
    if len(kids) == 4:
        c = create({'media_type': 'CAROUSEL', 'children': ','.join(kids), 'caption': CAR_CAP})
        out['create'] = c
        if 'id' in c:
            out['status'] = wait(c['id'], 30, 3)
            p = publish(c['id']); out['publish'] = p
            if 'id' in p: out['link'] = link(p['id'])
elif WHAT == 'story':
    c = create({'media_type': 'STORIES', 'image_url': RAW + 'story-tomorrow.jpg'})
    out['create'] = c
    if 'id' in c:
        out['status'] = wait(c['id'], 20, 3)
        p = publish(c['id']); out['publish'] = p
        if 'id' in p: out['link'] = link(p['id'])
print(json.dumps(out))
