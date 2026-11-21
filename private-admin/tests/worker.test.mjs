import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import {createHandler,configFromEnv} from "../src/index.js";

const root=resolve(dirname(fileURLToPath(import.meta.url)),"..");
const ENV={
  TEAM_DOMAIN:"https://sample.cloudflareaccess.com",
  POLICY_AUD:"a".repeat(64),
  ADMIN_EMAIL:"Owner@Example.org",
  ASSETS:{fetch:async request=>new Response("safe private asset",{
    status:200,headers:{"Content-Type":"text/plain","Access-Control-Allow-Origin":"*"}
  })}
};
const makeRequest=(path="/",token="jwt-placeholder",method="GET")=>
  new Request("https://naviboa-admin.example.workers.dev"+path,{
    method,
    headers:token?{"Cf-Access-Jwt-Assertion":token}:{}
  });
const accept=()=>({email:"owner@example.org"});

test("fails closed when JWT configuration or static asset binding is missing",async()=>{
  const app=createHandler(accept);
  assert.equal((await app.fetch(makeRequest(),{})).status,503);
  assert.equal((await app.fetch(makeRequest(),{...ENV,POLICY_AUD:""})).status,503);
  assert.equal((await app.fetch(makeRequest(),{...ENV,ADMIN_EMAIL:""})).status,503);
  assert.equal((await app.fetch(makeRequest(),{...ENV,ASSETS:undefined})).status,503);
  assert.equal(configFromEnv({...ENV,TEAM_DOMAIN:"https://evil.example"}),null);
  assert.equal(configFromEnv({...ENV,TEAM_DOMAIN:"http://sample.cloudflareaccess.com"}),null);
});

test("never serves an unauthenticated page, script or queue",async()=>{
  const app=createHandler(accept);
  for(const path of ["/","/index.html","/review.js","/data/review-queue.json"]){
    const res=await app.fetch(makeRequest(path,null),ENV);
    assert.equal(res.status,403,path);
  }
});

test("a forged or expired token does not pass",async()=>{
  const app=createHandler(async()=>{throw new Error("invalid token")});
  assert.equal((await app.fetch(makeRequest(),ENV)).status,403);
});

test("verified user not matching single admin email is forbidden",async()=>{
  const app=createHandler(async()=>({email:"somebody@example.org"}));
  assert.equal((await app.fetch(makeRequest("/review.css"),ENV)).status,403);
  const withoutEmail=createHandler(async()=>({}));
  assert.equal((await withoutEmail.fetch(makeRequest(),ENV)).status,403);
});

test("valid identity can access only allowed private assets",async()=>{
  const app=createHandler(accept);
  const res=await app.fetch(makeRequest("/"),ENV);
  assert.equal(res.status,200);
  assert.equal(await res.text(),"safe private asset");
  assert.equal(res.headers.get("Access-Control-Allow-Origin"),null);
  assert.match(res.headers.get("Cache-Control"),/no-store/);
  assert.match(res.headers.get("Content-Security-Policy"),/frame-ancestors 'none'/);
  assert.equal(res.headers.get("X-Robots-Tag"),"noindex, nofollow, noarchive");
  for(const path of ["/admin/review.html","/data/reviews.json","/scripts/quality.py","/secret","/favicon.ico"]){
    assert.equal((await app.fetch(makeRequest(path),ENV)).status,404,path);
  }
});

test("POST and HTTP are forbidden and HEAD contains no body",async()=>{
  const app=createHandler(accept);
  assert.equal((await app.fetch(makeRequest("/","jwt-placeholder","POST"),ENV)).status,405);
  const head=await app.fetch(makeRequest("/index.html","jwt-placeholder","HEAD"),ENV);
  assert.equal(head.status,200);
  assert.equal(await head.text(),"");
  const bad=new Request("http://naviboa-admin.example.workers.dev",{headers:{"Cf-Access-Jwt-Assertion":"jwt-placeholder"}});
  assert.equal((await app.fetch(bad,ENV)).status,403);
});

test("bundle contains only whitelisted dashboard assets, no review ledger",async()=>{
  const file=async path=>readFile(resolve(root,"dist",path),"utf8");
  const html=await file("index.html");
  assert.match(html,/Secure administrator portal/);
  assert.doesNotMatch(html,/127\.0\.0\.1/);
  assert.match(html,/noindex/);
  const js=await file("review.js");
  assert.match(js,/\/data\/review-queue\.json/);
  assert.doesNotMatch(js,/'\.\.\/data\/review-queue\.json'/);
  const queue=JSON.parse(await file("data/review-queue.json"));
  assert.ok(Array.isArray(queue.items));
  await assert.rejects(()=>file("data/reviews.json"),{code:"ENOENT"});
});
