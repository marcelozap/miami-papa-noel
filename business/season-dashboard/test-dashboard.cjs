'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
assert.equal(scripts.length, 1);
const source = scripts[0][1].replace(/var LEADS = \[[^\r\n]*\];/,
  'var LEADS = [{id:"lead-1",org:"Synthetic Organization",city:"Test City",group:"Test",srcfile:"synthetic",phone:"",email:""}];');
assert.notEqual(source, scripts[0][1], 'Use synthetic leads only');
new vm.Script(source);

// Pure JavaScript unit harness, NOT browser or file:// verification.
function harness(seed = {}, options = {}) {
  const nodes = new Map();
  const settings = {failSave:false, confirm:true, ...options};
  let raw = settings.raw === undefined ? JSON.stringify(seed) : settings.raw;
  let writes = 0, confirms = 0, alerts = 0;
  function element(id) {
    if (!nodes.has(id)) nodes.set(id, {value:'',textContent:'',innerHTML:'',events:{},
      classList:{toggle(){}},appendChild(){},querySelectorAll(){return [];},
      addEventListener(name, fn){this.events[name] = fn;}});
    return nodes.get(id);
  }
  const context = vm.createContext({
    document:{getElementById:element,querySelectorAll(){return [];},createElement(){return element('created');},addEventListener(){}},
    localStorage:{getItem(){return raw;},setItem(key,value){if(settings.failSave)throw new Error('Synthetic storage refusal');raw=value;writes++;}},
    navigator:{},window:{confirm(){confirms++;return settings.confirm;},alert(){alerts++;}},setTimeout(){},
    fetch(){throw new Error('Network is forbidden');},XMLHttpRequest(){throw new Error('Network is forbidden');},
    FileReader:function(){this.readAsText=function(file){this.result=file.text;this.onload();};}
  });
  vm.runInContext(source,context,{timeout:2000});
  return {context,settings,run:code=>vm.runInContext(code,context,{timeout:2000}),
    state:()=>JSON.parse(JSON.stringify(context.store)), raw:()=>raw, writes:()=>writes,
    confirms:()=>confirms,alerts:()=>alerts,message:()=>element('msg').textContent,
    csv:()=>context.buildCSV(), restore:text=>context.restoreCSV(text)};
}
const seed = {'chk:t1':true,'chk:t2':false,'st:lead-1':'Spoke to them','nt:lead-1':'Synthetic, "quoted"\r\nline two'};

test('exact v2 roundtrip preserves notes, false ticks, empty fields and BOM',()=>{
  for (const state of [seed,{}, {'chk:t1':false,'st:lead-1':'','nt:lead-1':''}]) {
    const original=harness(state), target=harness({'nt:lead-1':'prior synthetic'});
    assert.equal(target.restore('\uFEFF'+original.csv()),true);
    assert.deepEqual(target.state(),state);
    assert.deepEqual(JSON.parse(target.raw()),state);
    assert.equal(target.confirms(),1);
  }
});

test('complete old CSV export remains compatible',()=>{
  const h=harness();
  const csv='id,organisation,city,phone,email,source_file,status,notes\r\nlead-1,Synthetic,Test,,,synthetic,Spoke to them,legacy note\r\n__checklist__,t1,,,,,,\r\n';
  assert.equal(h.restore(csv),true);
  assert.deepEqual(h.state(),{'st:lead-1':'Spoke to them','nt:lead-1':'legacy note','chk:t1':true});
});

test('malformed, incomplete, duplicate and unknown imports preserve prior state',()=>{
  const head='id,organisation,city,phone,email,source_file,status,notes\r\n';
  const row='lead-1,Synthetic,Test,,,synthetic,Spoke to them,note\r\n';
  for(const csv of ['', 'id,status,notes\r\n',head,head+'unknown,,,,,,,\r\n',
    head+'lead-1,,,,,,Spoke to them,"unfinished',head+row,head+row+row,
    head+'lead-1,,,,,,bad-status,note\r\n__checklist__,,,,,,,',
    head+'lead-1,,,,,,Spoke to them,"note"junk',head+row+'__checklist__,unknown,,,,,,']) {
    const h=harness(seed), before=h.raw();
    assert.equal(h.restore(csv),false,csv);
    assert.deepEqual(h.state(),seed);
    assert.equal(h.raw(),before);
    assert.equal(h.writes(),0);
    assert.equal(h.confirms(),0);
  }
});

test('cancel never mutates memory or stored data',()=>{
  const h=harness(seed,{confirm:false}), before=h.raw();
  assert.equal(h.restore(harness({}).csv()),false);
  assert.deepEqual(h.state(),seed);assert.equal(h.raw(),before);assert.equal(h.writes(),0);
});

test('failed persistence never reports restored or replaces the current state',()=>{
  const h=harness(seed,{failSave:true}), before=h.raw();
  assert.equal(h.restore(harness({}).csv()),false);
  assert.deepEqual(h.state(),seed);assert.equal(h.raw(),before);
  assert.match(h.message(),/NOT SAVED/);
});

test('notes save failure alerts and retains unsaved edits and the prior saved copy',()=>{
  const h=harness(seed,{failSave:true}), before=h.raw();
  h.run('store["nt:lead-1"]="synthetic unsaved edit";saveEdit();');
  assert.equal(h.state()['nt:lead-1'],'synthetic unsaved edit');
  assert.equal(h.raw(),before);assert.equal(h.alerts(),1);assert.match(h.message(),/NOT SAVED/);
  const restored=harness();assert.equal(restored.restore(h.csv()),true);
  assert.equal(restored.state()['nt:lead-1'],'synthetic unsaved edit');
});

test('unreadable saved state is not overwritten at startup or during edits',()=>{
  const h=harness({}, {raw:'{broken synthetic'});
  assert.equal(h.writes(),0);
  h.run('store["nt:lead-1"]="synthetic";saveEdit();');
  assert.equal(h.raw(),'{broken synthetic');assert.equal(h.writes(),0);
});

test('spreadsheet prefixes are neutralized without losing original notes',()=>{
  for(const note of ['=1+1','+1','-1','@SUM(1)','\t=1','\r=1','\n=1','  =1',"'original",'normal']) {
    const h=harness({'nt:lead-1':note}), csv=h.csv();
    const rows=h.context.parseCSV(csv);
    const cell=rows.find(r=>r[0]==='lead-1')[7];
    if(note!=='normal') assert.equal(cell[0],"'");
    const target=harness();assert.equal(target.restore(csv),true);
    assert.equal(target.state()['nt:lead-1'],note);
  }
});

test('modified metadata, prototype keys and oversized files are rejected',()=>{
  const original=harness(seed).csv();
  for (const csv of [original.replace('Spoke to them','Not this year'), 'x'.repeat(2*1024*1024+1)]) {
    const h=harness(seed);assert.equal(h.restore(csv),false);assert.equal(h.writes(),0);
  }
  const h=harness();
  assert.throws(()=>h.context.validateState(JSON.parse('{"__proto__":{}}')));
});
