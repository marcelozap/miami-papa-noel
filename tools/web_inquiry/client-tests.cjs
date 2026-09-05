'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

class Element {
  constructor(tag='div') {
    this.tagName=tag; this.children=[]; this.listeners={}; this.dataset={};
    this.hidden=false; this.value=''; this.textContent=''; this.attributes={};
    this.classList={toggle(){}};
  }
  append(...items) { this.children.push(...items); }
  prepend(...items) { this.children.unshift(...items); }
  replaceChildren(...items) { this.children=[...items]; }
  setAttribute(key,value) { this.attributes[key]=value; }
  addEventListener(name,handler) { this.listeners[name]=handler; }
  querySelector(selector) {
    const all=this.children.flatMap(child=>[child,...descendants(child)]);
    if(selector.includes('reply-language')) return all.find(child=>child.name==='reply-language'&&child.checked);
    return all.find(child=>child.tagName==='button') || new Element('button');
  }
}
function descendants(element) {
  return (element.children||[]).flatMap(child=>[child,...descendants(child)]);
}
function response(data,ok=true) { return {ok,json:async()=>data}; }
function harness() {
  const elements=new Map(), requests=[];
  const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
  get('desk').hidden=true;
  const context=vm.createContext({
    document:{documentElement:{dataset:{}},getElementById:get,createElement:tag=>new Element(tag)},
    location:{pathname:'/operator'},crypto:{randomUUID:()=> 'synthetic-key'},
    AbortController,DOMException,console,confirm:()=>true,
    navigator:{clipboard:{writeText:async()=>{}}},
    fetch:(url,options)=>url==='/health'?Promise.resolve(response({mode:'demo'})):
      new Promise((resolve,reject)=>requests.push({url,options,resolve,reject})),
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname,'app.js'),'utf8'),context);
  return {get,requests,context,run:code=>vm.runInContext(code,context)};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function item(name='Synthetic Family') {
  return {id:'synthetic-id',customer:{name,contact:'synthetic@example.invalid',message:'Synthetic inquiry'},
    status:'queued',received_at:'2026-09-04T23:00:00Z',record:null};
}
function listing(items) { return response({live:false,next_cursor:null,items}); }
function quiet(promise) {
  return promise.catch(error=>assert.equal(error.name,'AbortError'));
}

test('a delayed refresh cannot restore customer data after logout',async()=>{
  const h=harness(); h.run("token='synthetic-token';reviewer='Synthetic Operator'");
  const pending=quiet(h.run('load()'));
  h.get('logout').onclick();
  assert.equal(h.requests[0].options.signal.aborted,true);
  h.requests[0].resolve(listing([item()]));
  await pending;
  assert.equal(h.get('desk').hidden,true);
  assert.equal(h.get('login').hidden,false);
  assert.equal(h.get('queue').children.length,0);
  assert.equal(h.get('detail').children.length,0);
  assert.equal(h.run('items.length'),0);
});

test('an old login response cannot replace a newer login session',async()=>{
  const h=harness(); h.run("token='old-synthetic-token';reviewer='Old Operator'");
  const old=quiet(h.run('load()'));
  h.get('logout').onclick();
  h.get('token').value='new-synthetic-token'; h.get('reviewer').value='New Operator';
  h.get('login').listeners.submit({preventDefault(){},currentTarget:h.get('login')});
  h.requests[1].resolve(listing([item('New Session')])); await tick();
  h.requests[0].resolve(listing([item('Old Session')])); await old; await tick();
  assert.equal(h.run('items[0].customer.name'),'New Session');
  assert.equal(h.run('token'),'new-synthetic-token');
});

test('a slower refresh cannot overwrite the newest displayed queue',async()=>{
  const h=harness(); h.run("token='synthetic-token';reviewer='Synthetic Operator'");
  const old=quiet(h.run('load()')), current=quiet(h.run('load()'));
  h.requests[1].resolve(listing([item('Current')])); await current;
  h.requests[0].resolve(listing([item('Stale')])); await old;
  assert.equal(h.run('items[0].customer.name'),'Current');
});

test('approval sends the exact revision and inquiry that were displayed',async()=>{
  const h=harness(); h.run("token='synthetic-token';reviewer='Synthetic Operator'");
  const displayed={...item(),status:'draft_ready',draft_revision:'a'.repeat(64),
    record:{language:'es',draft_en:'Synthetic English',draft_es:'Synthetic Spanish',fallback_used:true,validation:[]}};
  const loaded=h.run('load()'); h.requests[0].resolve(listing([displayed])); await loaded;
  const approve=descendants(h.get('detail')).find(node=>node.textContent==='Approve draft / Aprobar borrador');
  const clicked=approve.onclick();
  const sent=JSON.parse(h.requests[1].options.body);
  assert.equal(sent.id,displayed.id);
  assert.equal(sent.draft_revision,displayed.draft_revision);
  assert.equal(sent.language,'es');
  h.requests[1].resolve(response({status:'approved'})); await tick();
  h.requests[2].resolve(listing([{...displayed,status:'approved',reviewed_language:'es'}]));
  await clicked;
});

test('an action completing after logout does not reopen the queue',async()=>{
  const h=harness(); h.run("token='synthetic-token';reviewer='Synthetic Operator';selected='synthetic-id'");
  const button=h.run("action('Generate','/api/draft')");
  const clicked=button.onclick();
  h.get('logout').onclick();
  h.requests[0].resolve(response({status:'draft_ready'}));
  await clicked;
  assert.equal(h.requests.length,1);
  assert.equal(h.get('desk').hidden,true);
  assert.equal(h.get('operator-result').textContent,'Signed out / Sesión cerrada');
});
