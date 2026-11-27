"""Ripmatic Black Friday single card posts, Fri Nov 27, 2026: publishes the one Instagram post that is due now. Stateless.
  IG_CRED=<credential handle> python3 bf_post.py [--dry]
Picks the manifest entry whose time is between 4 minutes ahead and 22 minutes ago (Pacific). Skips it when the same caption is already live on
@ripmatics, or when the card is no longer listed at the full 15% Black Friday price on ripmatic.com (sold). Prints one JSON line."""
import os, sys, json, time, subprocess, datetime as dt, urllib.request
from zoneinfo import ZoneInfo
H = os.path.dirname(os.path.abspath(__file__)); PT = ZoneInfo('America/Los_Angeles')
CRED = os.environ['IG_CRED']; IG = '17841421327198362'; B = 'https://graph.instagram.com/v23.0'
RAW = os.environ.get('BF_RAW', '')  # https://raw.githubusercontent.com/<repo>/<sha>/bf1127/
def call(a):
    r = subprocess.run(['pplx', 'credentials', 'run', CRED, '--', 'curl', '-s'] + a, capture_output=True, text=True)
    try: return json.JSONDecoder().raw_decode(r.stdout)[0]
    except Exception: return {'raw': r.stdout[:300], 'err': r.stderr[:300]}
def out(**k): print(json.dumps(k)); sys.exit()
now = dt.datetime.now(PT); M = json.load(open(os.path.join(H, 'manifest.json'))); due = None
for e in M:
    late = (now - dt.datetime.strptime(e['at'], '%Y-%m-%dT%H:%M').replace(tzinfo=PT)).total_seconds() / 60
    if -4 <= late <= 22: due = e
if not due: out(result='none_due', now=now.strftime('%H:%M PT'))
m = call([f'{B}/me/media', '--get', '--data-urlencode', 'fields=id,permalink,caption,timestamp', '--data-urlencode', 'limit=20'])
if 'data' not in m: out(result='error', step='recent', name=due['name'], detail=m)
for x in m['data']:
    if (x.get('caption') or '')[:50] == due['caption'][:50]: out(result='already_live', name=due['name'], permalink=x.get('permalink'))
req = urllib.request.Request('https://ripmatic.com/api/shop', headers={'User-Agent': 'Mozilla/5.0 ripmatic-social'})
shop = {x['slotId']: x for x in json.load(urllib.request.urlopen(req, timeout=30))}; l = shop.get(due['sku'])
if not l or l.get('saleCents') != int(l['priceCents'] * 85 / 100 / 100 + 0.5) * 100: out(result='skipped_sold', name=due['name'], at=due['at'])
if '--dry' in sys.argv: out(result='dry', name=due['name'], at=due['at'], image=RAW + due['file'])
c = call(['-X', 'POST', f'{B}/{IG}/media', '--data-urlencode', 'image_url=' + RAW + due['file'], '--data-urlencode', 'caption=' + due['caption']])
if 'id' not in c: out(result='error', step='create', name=due['name'], detail=c)
s = {}
for _ in range(40):
    s = call([f'{B}/{c["id"]}?fields=status_code'])
    if s.get('status_code') in ('FINISHED', 'ERROR', 'EXPIRED'): break
    time.sleep(4)
if s.get('status_code') != 'FINISHED': out(result='error', step='status', name=due['name'], detail=s)
p = call(['-X', 'POST', f'{B}/{IG}/media_publish', '--data-urlencode', 'creation_id=' + c['id']])
if 'id' not in p:
    time.sleep(10)
    for x in call([f'{B}/me/media?fields=id,permalink,caption&limit=3']).get('data', []):
        if (x.get('caption') or '')[:50] == due['caption'][:50]: out(result='posted', name=due['name'], permalink=x.get('permalink'), note='publish returned an error but the post is live')
    out(result='error', step='publish', name=due['name'], detail=p)
out(result='posted', name=due['name'], at=due['at'], permalink=call([f'{B}/{p["id"]}?fields=permalink']).get('permalink'))
