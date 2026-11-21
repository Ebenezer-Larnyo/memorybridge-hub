/**
 * Rebuild a SMALL, explicitly whitelisted asset bundle for an Access-protected
 * Cloudflare Worker. Never copy the full repo or the human review ledger.
 */
import {readFile,writeFile,mkdir,rm,copyFile} from "node:fs/promises";
import {resolve,dirname,join} from "node:path";
import {fileURLToPath} from "node:url";

const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,"../..","..");
const dest=resolve(here,"../dist");
const read=path=>readFile(resolve(root,path),"utf8");
async function put(name,text){
  const target=join(dest,name);
  await mkdir(dirname(target),{recursive:true});
  await writeFile(target,text,"utf8");
}
function replaceRequired(text,from,to,label){
  if(!text.includes(from))throw new Error("Missing required "+label);
  return text.replaceAll(from,to);
}

await rm(dest,{recursive:true,force:true});
await mkdir(dest,{recursive:true});

let html=await read("admin/review.html");
html=replaceRequired(html,"../favicon.svg","favicon.svg","favicon");
html=replaceRequired(html,"../index.html","https://ebenezer-larnyo.github.io/memorybridge-hub/","public hub");
html=replaceRequired(html,"../data/quality-report.json","/data/quality-report.json","quality report");
html=replaceRequired(html,
  "Locally hosted administrator workspace — not deployed on the public Naviboa website.",
  "Secure administrator portal — signed-in access only.","admin notice");
html=replaceRequired(html,"Use only on your own computer at 127.0.0.1.",
  "Cloudflare Access verifies your identity before the dashboard loads.","local-only notice");
html=html.replace("The GitHub issue and repository review record are still public. The GitHub issue and review record are public.",
  "Submitted GitHub issues and repository review records remain public.");
html=replace("<head>","<head>\n<meta name=\"robots\" content=\"noindex,nofollow,noarchive\">");
html=html.replace("REVIEWER WORKSPACE · V4.2","PRIVATE ADMIN · V4.4");
await put("index.html",html);

let js=await read("admin/review.js");
js=replaceRequired(js,"'../data/resources.json'","'/data/resources.json'","directory route");
js=replaceRequired(js,"'../data/review-queue.json'","'/data/review-queue.json'","review queue route");
js=replaceRequired(js,"'../data/quality-index.json'","'/data/quality-index.json'","review index route");
await put("review.js",js);
await put("review.css",await read("admin/review.css"));
await copyFile(resolve(root,"favicon.svg"),join(dest,"favicon.svg"));
for(const asset of ["resources.json","review-queue.json","quality-index.json","quality-report.json"]){
  const text=await read("data/"+asset);
  const data=JSON.parse(text);
  if(!data || typeof data !== "object")throw new Error("Invalid review data: "+asset);
  await put("data/"+asset,JSON.stringify(data));
}
console.log("Built restricted review portal: dashboard, 3 frontend assets, 4 JSON snapshots.");
console.log("No human review ledger or GitHub credentials included.");
