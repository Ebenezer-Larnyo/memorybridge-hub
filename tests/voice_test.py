"""Voice and AI-answer behavior tests using mocked browser speech APIs and a mocked Worker."""
import os,json
from playwright.sync_api import sync_playwright,expect
base=os.environ.get('TEST_URL','http://127.0.0.1:8000/')
FAKE_SR="""
window.__sr={};
class FakeSR{start(){const m=window.__srMode||'ok';setTimeout(()=>{this.onstart&&this.onstart();
 if(m==='ok'){this.onresult({results:[[{transcript:'respite care'}]]});setTimeout(()=>this.onend&&this.onend(),20)}
 else{this.onerror({error:m});setTimeout(()=>this.onend&&this.onend(),20)}},10)}
 stop(){this.onend&&this.onend()} abort(){this.onend&&this.onend()}}
window.SpeechRecognition=FakeSR;
"""
FAKE_SYNTH="""
window.__spoken=[];window.__cancels=0;
window.SpeechSynthesisUtterance=function(t){this.text=t};
Object.defineProperty(window,'speechSynthesis',{value:{speaking:false,pending:false,getVoices:()=>[],addEventListener(){},speak(u){window.__spoken.push(u.text);this.speaking=true},cancel(){window.__cancels++;this.speaking=false}},configurable:true});
"""
with sync_playwright() as p:
    b=p.chromium.launch()
    def page_with(script,endpoint=None):
        pg=b.new_page(viewport={'width':390,'height':844});errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        if endpoint:pg.add_init_script("window.MIRA_ENDPOINT='%s'"%endpoint)
        pg.add_init_script(script);pg.goto(base)
        expect(pg.locator('#results article')).not_to_have_count(0,timeout=15000);return pg,errs
    # 1. unsupported browser: clear explanation, no crash
    pg,errs=page_with("delete window.SpeechRecognition;delete window.webkitSpeechRecognition;")
    expect(pg.locator('#voice-status')).to_contain_text('not available')
    pg.locator('#mira-mic').click();expect(pg.locator('#voice-status')).to_contain_text('keyboard');assert not errs,errs
    # 2. consent required, then transcript fills input
    pg,errs=page_with(FAKE_SR)
    pg.locator('#mira-mic').click();expect(pg.locator('#voice-status')).to_contain_text('tick the box')
    pg.locator('#mic-consent').check();pg.locator('#mira-mic').click()
    expect(pg.locator('#mira-input')).to_have_value('respite care');expect(pg.locator('#voice-status')).to_contain_text('Find resources');assert not errs,errs
    # 3. specific error messages
    for code,msg in [('not-allowed','blocked'),('service-not-allowed','Dictation'),('no-speech','did not hear')]:
        pg,errs=page_with(FAKE_SR+"window.__srMode='%s';"%code)
        pg.locator('#mic-consent').check();pg.locator('#mira-mic').click();expect(pg.locator('#voice-status')).to_contain_text(msg)
    # 4. read aloud speaks sentence by sentence; stop cancels
    pg,errs=page_with(FAKE_SYNTH)
    pg.locator('#mira-input').fill('respite care');pg.locator('#mira-form button[type=submit]').click()
    expect(pg.locator('#mira-links article')).not_to_have_count(0)
    pg.locator('#mira-speak').click();expect(pg.locator('#voice-status')).to_contain_text('Reading aloud')
    spoken=pg.evaluate('window.__spoken');assert len(spoken)>=2 and ' '.join(spoken).startswith('Here are resources'),spoken
    pg.locator('#mira-stop').click();assert pg.evaluate('window.__cancels')>=1;assert not errs,errs
    # 5. read aloud when speech is missing
    pg,errs=page_with("delete window.speechSynthesis;");pg.locator('#mira-speak').click();expect(pg.locator('#voice-status')).to_contain_text('not available')
    # 6. AI answers: consent gate, request shape, summary shown with disclosure
    EP='https://worker.test/';seen=[]
    def handler(route):
        req=route.request
        if req.method=='OPTIONS':route.fulfill(status=204,headers={'access-control-allow-origin':'*','access-control-allow-headers':'authorization,content-type','access-control-allow-methods':'POST,OPTIONS'});return
        seen.append(req.post_data_json|{'auth':req.headers.get('authorization')})
        route.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps({'selection':[0],'reply':'Respite care gives caregivers short breaks.'}))
    pg,errs=page_with("",EP);pg.route(EP,handler)
    pg.locator('#ai-mode').select_option('cloud');pg.locator('#pilot-code').fill('pilot-123')
    pg.locator('#mira-input').fill('I need a break from caring for my mom');pg.locator('#mira-form button[type=submit]').click()
    expect(pg.locator('#ai-state')).to_contain_text('unavailable');assert not seen,'must not call the Worker without consent'
    pg.locator('#cloud-consent').check();pg.locator('#mira-input').fill('I need a break from caring for my mom');pg.locator('#mira-form button[type=submit]').click()
    expect(pg.locator('#mira-reply')).to_contain_text('AI-written summary');expect(pg.locator('#mira-reply')).to_contain_text('short breaks');expect(pg.locator('#mira-reply')).to_contain_text('not medical advice')
    assert seen and seen[0]['auth']=='Bearer pilot-123' and 'description' in seen[0]['candidates'][0] and seen[0]['question'].startswith('I need a break'),seen
    # 7. emergency never calls the Worker
    seen.clear();pg.locator('#mira-input').fill('she wandered off');pg.locator('#mira-form button[type=submit]').click()
    expect(pg.locator('#mira-reply')).to_contain_text('911');assert not seen;assert not errs,errs
    b.close()
print('Voice and AI answer tests passed')
