"""Bounded same-host discovery; no forum content."""
import json,time,re,datetime,urllib.robotparser,urllib.parse as U
from pathlib import Path
import requests
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parents[1]/'data'
AGENT='MemoryBridgeHubBot'
HEAD={'User-Agent':AGENT+' (research directory; github.com/Ebenezer-Larnyo/memorybridge-hub)'}
RULES={'Symptoms':r'symptom|memory loss|warning sign|behavio[u]?r','Diagnosis':r'diagnos|screening|assessment','Daily care':r'daily care|everyday care|home care|communication|routine|hospice','Caregiver support':r'caregiv|carer|care partner','Emotional support':r'grief|stress|mental health|burnout|emotional','Respite & services':r'respite|local service|day care|long.term care|nursing home','Treatment & medication':r'treatment|medication|medicine|drug','Lifestyle & wellbeing':r'lifestyle|exercise|nutrition|wellbeing','Assistive technology':r'assistive|technology|memory aid|safety device','Financial & legal':r'financial|legal|insurance|costs|benefits','Peer support':r'support group|peer support','Stigma & inclusion':r'stigma|equity|diversity|cultural|inclusion','COVID & dementia':r'covid|coronavirus','Research & awareness':r'research|statistics|awareness|prevalence'}
def classify(s):return [k for k,v in RULES.items() if re.search(v,s,re.I)]
def canonical(url):
 p=U.urlsplit(url);return U.urlunsplit((p.scheme,p.netloc,p.path or '/','',''))
def allowed(url,host):
 p=U.urlsplit(url);return p.scheme=='https' and p.netloc==host and not re.search(r'login|sign.in|forum|community/post|donat|\.pdf$|\.jpg$|\.png$',p.path,re.I)
def main():
 entries={canonical(x['url']):x for x in json.loads((DATA/'resources.json').read_text())['resources']}
 sources=json.loads((DATA/'sources.json').read_text());day=datetime.date.today().isoformat();report=[];robots={};last={};session=requests.Session()
 def get(url,host):
  if not allowed(url,host):return None
  if host not in robots:
   rr=session.get('https://'+host+'/robots.txt',headers=HEAD,timeout=15,allow_redirects=False);rp=urllib.robotparser.RobotFileParser()
   if rr.status_code==404:rp.parse(['User-agent: *','Disallow:'])
   elif rr.status_code==200:rp.parse(rr.text.splitlines())
   else:rp.parse(['User-agent: *','Disallow: /'])
   robots[host]=rp;last[host]=time.monotonic()
  rp=robots[host]
  if not rp.can_fetch(AGENT,url):return None
  rate=rp.request_rate(AGENT) or rp.request_rate('*')
  delay=max(2,rp.crawl_delay(AGENT) or rp.crawl_delay('*') or 0,rate.seconds/rate.requests if rate and rate.requests else 0)
  time.sleep(max(0,delay-(time.monotonic()-last[host])));last[host]=time.monotonic()
  with session.get(url,headers=HEAD,timeout=20,allow_redirects=False,stream=True) as response:
   if response.status_code in (429,503):
    robots[host]=urllib.robotparser.RobotFileParser();robots[host].parse(['User-agent: *','Disallow: /']);return None
   if response.status_code!=200 or 'text/html' not in response.headers.get('Content-Type','').lower():return None
   buf=bytearray()
   for chunk in response.iter_content(65536):
    buf.extend(chunk)
    if len(buf)>2000000:return None
   return BeautifulSoup(bytes(buf),'html.parser')
 for source in sources:
  seed=canonical(source['url']);host=U.urlsplit(seed).netloc
  try:
   page=get(seed,host)
   if page is None:report.append({'url':seed,'result':'Skipped or unavailable'});continue
   if seed in entries:
    entries[seed]['checked']=day
    if entries[seed].get('status')!='Human reviewed':entries[seed]['status']='Link checked; content not reviewed'
   candidates=[]
   for a in page.select('a[href]'):
    label=' '.join(a.stripped_strings);url=canonical(U.urljoin(seed,a['href']))
    if 12<=len(label)<=180 and classify(label) and allowed(url,host) and url not in entries and url not in candidates:candidates.append(url)
   if candidates:
    offset=(datetime.date.today().toordinal()*4)%len(candidates)
    candidates=candidates[offset:]+candidates[:offset]
   for url in candidates[:4]:
    child=get(url,host)
    if child is None:continue
    title=child.title.get_text(' ',strip=True)[:180] if child.title else ''
    tags=classify(title+' '+U.urlsplit(url).path)
    if not title or not tags or not re.search(r'dementia|alzheimer|caregiv|carer|aging|ageing|memory',title+' '+url,re.I):continue
    entries[url]=dict(title=title,url=url,organization=source['organization'],region=source['region'],kind=source['kind'],topics=tags,language=source.get('language','Not tagged'),description='Automatically discovered resource. Visit the original source for details.',status='Automatically discovered; not reviewed',checked=day)
   report.append({'url':seed,'result':'Checked'})
  except Exception as exc:report.append({'url':seed,'result':type(exc).__name__})
 (DATA/'crawl-report.json').write_text(json.dumps({'date':day,'sources':report},indent=2));(DATA/'resources.json').write_text(json.dumps({'updated':day,'resources':list(entries.values())},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
