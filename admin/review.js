'use strict';
const REPO='Ebenezer-Larnyo/memorybridge-hub';
const FENCE=String.fromCharCode(96).repeat(3);
const CRITERIA=[
 ['source_identity','Source identity and credibility'],
 ['topic_relevance','Topic and audience relevance'],
 ['description_accuracy','Directory description accuracy'],
 ['currency','Information currency'],
 ['geographic_fit','Geographic and service applicability'],
 ['language_verified','Language verified on source'],
 ['accessibility_spotcheck','Accessibility spot-check'],
 ['medical_safety_screen','Medical safety and misleading claims']
];
const $=id=>document.getElementById(id);
let directory=[],priority=[],index={},audit={},selected=null,visibleCount=12;
function text(id,value){$(id).textContent=String(value)}
function showStatus(message,error=false){text('form-status',message);$('form-status').classList.toggle('error',error)}
function urlKey(u){try{const x=new URL(u);return x.protocol==='https:'?x.href.replace(/\/$/,''):''}catch{return ''}}
function dataFor(item){return index[item.url]||index[urlKey(item.url)]||null}
function humanStatus(item){const r=dataFor(item);if(!r)return 'Awaiting human review';if(r.decision==='approved'&&r.review_due)return 'Review due';return r.decision==='approved'?'Human reviewed':r.decision==='needs_revision'?'Correction requested':'Excluded'}
function flagName(x){return ({description_placeholder:'Description incomplete',language_not_tagged:'Language not tagged',link_not_recently_checked:'Link not recently checked',no_human_review:'Human review pending',review_expired:'Review expired',correction_requested:'Correction requested'})[x]||x.replaceAll('_',' ')}
function listItems(){const q=$('search').value.toLowerCase().trim();const source=$('scope').value==='queue'?priority:directory;
 return source.filter(x=>{const hay=[x.title,x.organization,x.region,x.url,(x.topics||[]).join(' ')].join(' ').toLowerCase();return !q||q.split(/\s+/).every(word=>hay.includes(word))})}
function renderList(reset=false){
 if(reset)visibleCount=12;
 const items=listItems();text('queue-count',items.length+' matching');
 const panel=$('resource-list');panel.replaceChildren();
 for(const item of items.slice(0,visibleCount)){
  const b=document.createElement('button');b.type='button';b.className='item';b.setAttribute('aria-pressed',String(!!selected&&selected.url===item.url));
  const title=document.createElement('span');title.className='item-title';title.textContent=item.title||item.url;
  const detail=document.createElement('span');detail.className='item-meta';detail.textContent=(item.organization||'Source not tagged')+' · '+(item.region||'Region unknown')+' · '+humanStatus(item);
  b.append(title,detail);b.addEventListener('click',()=>choose(item));panel.append(b);
 }
 $('more').hidden=items.length<=visibleCount;
 if(!items.length)panel.textContent='No resources match these filters.';
}
function choose(item){
 selected=item;
 $('empty').hidden=true;$('selection').hidden=false;
 text('selected-title',item.title);text('selected-meta',[item.organization,item.region,(item.topics||[]).slice(0,3).join(', ')].filter(Boolean).join(' · '));
 $('original-link').href=item.url;text('selected-description',item.description&&!/^(Visit (the original|source)|Automatically discovered)/i.test(item.description)?item.description:'Description needs verification on the original source.');
 const flags=$('selected-flags');flags.replaceChildren();
 const tags=(priority.find(x=>x.url===item.url)||{}).flags||[];
 for(const v of tags){const s=document.createElement('span');s.className='flag';s.textContent=flagName(v);flags.append(s)}
 text('existing-status','Current status: '+humanStatus(item)+'. A link check is not a content review.');
 $('review-form').reset();$('evidence').value=item.url;$('replace-wrap').hidden=!dataFor(item);
 document.querySelectorAll('[data-criterion]').forEach(s=>s.value='');
 showStatus('Complete the checklist and add evidence-based notes before submitting.');
 renderList();$('inspect-heading').scrollIntoView({block:'nearest',behavior:'instant'});
}
function buildReview(){
 if(!selected)throw Error('Choose a resource first.');
 const criteria={};
 for(const [id,label] of CRITERIA){const v=document.querySelector('[data-criterion="'+id+'"]').value;if(!['pass','concern','not_applicable'].includes(v))throw Error('Complete every review criterion: '+label);criteria[id]=v}
 const d=$('decision').value;
 if(!['approved','needs_revision','excluded'].includes(d))throw Error('Select a review decision.');
 if(d==='approved'&&Object.values(criteria).some(x=>x!=='pass'))throw Error('Approval requires all eight checks to pass.');
 if(d==='needs_revision'&&!Object.values(criteria).includes('concern'))throw Error('Needs correction requires at least one concern.');
 const notes=$('notes').value.trim();
 if(notes.length<30||notes.length>1200)throw Error('Provide 30–1200 characters of concrete, non-confidential review notes.');
 const evidence=$('evidence').value.trim();
 if(!urlKey(evidence))throw Error('Evidence must use a valid public HTTPS URL.');
 if(!$('ack').checked)throw Error('Confirm that you inspected the source and will not submit confidential information.');
 const exists=!!dataFor(selected);
 if(exists&&!$('replace').checked)throw Error('An existing review is recorded; confirm replacement before submitting.');
 return {url:selected.url,evidence_url:evidence,decision:d,notes,criteria,replace_existing:exists};
}
function openIssue(review){
 const body='NAVIBOA_REVIEW_V1\n'+FENCE+'json\n'+JSON.stringify(review)+'\n'+FENCE;
 const url=new URL('https://github.com/'+REPO+'/issues/new');
 url.searchParams.set('title','Naviboa resource review: '+(selected.title||'Resource').slice(0,90));
 url.searchParams.set('body',body);
 window.open(url.href,'_blank','noopener,noreferrer');
 showStatus('GitHub has been opened. Sign in and select Submit new issue to send the review. Nothing has been approved yet.');
}
function download(review){
 const blob=new Blob([JSON.stringify(review,null,2)+'\n'],{type:'application/json'});
 const href=URL.createObjectURL(blob),a=document.createElement('a');a.href=href;a.download='naviboa-review-'+Date.now()+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(href),1000);
 showStatus('Review record downloaded. A downloaded file is not an approval or a GitHub submission.');
}
async function load(){
 try{
 const paths=['../data/resources.json','../data/review-queue.json','../data/quality-index.json'];
 const arr=await Promise.all(paths.map(p=>fetch(p,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Could not retrieve '+p);return r.json()})));
 directory=arr[0].resources||[];priority=arr[1].items||[];index=arr[2].review_index||{};audit=arr[2].stats||{};
 if(!Array.isArray(directory)||!Array.isArray(priority)||!directory.length)throw Error('Review directory was empty');
 text('stat-total',audit.total??directory.length);text('stat-awaiting',audit.awaiting_review??'—');text('stat-reviewed',audit.human_reviewed_current??0);text('stat-metadata',audit.descriptions_missing??'—');
 text('load-status','Loaded '+directory.length+' directory records and '+priority.length+' prioritized review candidates. Review decisions are still made by people.');
 renderList(true);
 }catch(e){text('load-status','Could not load the review directory: '+e.message+'. Refresh the page or check the public resource report.');}
}
const criteriaList=$('criteria');
for(const [key,title] of CRITERIA){
 const row=document.createElement('div');row.className='criterion';
 const label=document.createElement('label'),sel=document.createElement('select');sel.dataset.criterion=key;sel.id='criterion-'+key;label.htmlFor=sel.id;label.textContent=title;sel.required=true;
 for(const [value,txt] of [['','Choose assessment'],['pass','Pass'],['concern','Concern'],['not_applicable','Not applicable']]){const o=document.createElement('option');o.value=value;o.textContent=txt;sel.append(o)}
 row.append(label,sel);criteriaList.append(row);
}
$('search').addEventListener('input',()=>renderList(true));$('scope').addEventListener('change',()=>renderList(true));
$('more').addEventListener('click',()=>{visibleCount+=12;renderList()});
$('review-form').addEventListener('submit',e=>{e.preventDefault();try{const review=buildReview();openIssue(review)}catch(err){showStatus(err.message,true)}});
$('export-json').addEventListener('click',()=>{try{download(buildReview())}catch(err){showStatus(err.message,true)}});
load();
