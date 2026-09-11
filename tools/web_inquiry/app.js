'use strict';
document.documentElement.dataset.view = location.pathname === '/operator' ? 'operator' : 'inquiry';
const $ = id => document.getElementById(id);
let token = '', reviewer = '', selected = null, items = [], live = false, nextCursor = null;
let session = 0, loadVersion = 0;
const operatorRequests = new Set();
let requestKey = crypto.randomUUID(), lastSubmission = '';
const states = {queued:'New / Nueva',drafting:'Drafting / Generando',failed:'Draft failed / Falló el borrador',blocked:'Blocked / Bloqueada',draft_ready:'Review needed / Requiere revisión',approved:'Approved; not sent / Aprobada; sin enviar',sent:'Manual send recorded / Envío manual registrado',rejected:'Rejected / Rechazada'};
function notice(id, text, error=false) { $(id).textContent=text; $(id).className=error?'error':''; }
function node(tag, text, className='') { const el=document.createElement(tag); el.textContent=text; el.className=className; return el; }
async function api(path, body, auth=false) {
  const epoch=session, controller=auth?new AbortController():null;
  if(auth&&!token) throw new DOMException('Signed out','AbortError');
  const headers={};
  if(body!==undefined) headers['Content-Type']='application/json';
  if(auth) headers.Authorization='Bearer '+token;
  if(controller) operatorRequests.add(controller);
  try {
    const res=await fetch(path,{method:body===undefined?'GET':'POST',headers,body:body===undefined?undefined:JSON.stringify(body),signal:controller?.signal});
    const data=await res.json();
    if(auth&&epoch!==session) throw new DOMException('Session changed','AbortError');
    if(!res.ok) throw new Error(data.error||'Request failed / Falló la solicitud');
    return data;
  } finally { if(controller) operatorRequests.delete(controller); }
}
async function busy(button, work, resultId) {
  const epoch=session;
  button.disabled=true;
  try { await work(); } catch(e) {
    if(e.name!=='AbortError'&&(resultId!=='operator-result'||epoch===session)) notice(resultId,e.message||'Connection failed / Falló la conexión',true);
  }
  finally { button.disabled=false; }
}
async function load(older=false) {
  const epoch=session, version=++loadVersion;
  const pages = older ? 1 : Math.max(1,Math.ceil(items.length/100));
  let gathered = older ? items : [], cursor = older ? nextCursor : null, nextLive=live;
  for(let page=0;page<pages;page++) {
    const data=await api('/api/inquiries'+(cursor?'?before='+cursor:''),undefined,true);
    if(epoch!==session||version!==loadVersion) throw new DOMException('Superseded refresh','AbortError');
    gathered=gathered.concat(data.items); nextLive=data.live; cursor=data.next_cursor;
    if(!cursor)break;
  }
  items=gathered;nextCursor=cursor;live=nextLive;
  $('older').hidden=!nextCursor;
  $('login').hidden=true; $('desk').hidden=false;
  $('count').textContent=items.length+(items.length===1?' request / solicitud':' requests / solicitudes');
  $('queue').replaceChildren();
  for(const item of items) {
    const button=node('button',item.customer.name,'queue-item'); button.type='button';
    button.setAttribute('aria-pressed',String(item.id===selected));
    button.append(node('span',states[item.status]||item.status),node('span',new Date(item.received_at).toLocaleString()));
    button.onclick=()=>{selected=item.id;render();}; $('queue').append(button);
  }
  if(!selected&&items.length) selected=items[0].id;
  render();
}
function action(label, path, details={}) {
  const identifier=selected;
  const b=node('button',label); b.type='button';
  b.onclick=()=>busy(b,async()=>{
    const result=await api(path,{id:identifier,reviewer,...details},true);
    notice('operator-result',states[result.status]||'Saved / Guardado'); await load();
  },'operator-result'); return b;
}
function render() {
  const item=items.find(x=>x.id===selected);
  for(const b of $('queue').children) b.setAttribute('aria-pressed',String(items[Array.from($('queue').children).indexOf(b)]?.id===selected));
  const detail=$('detail'); detail.replaceChildren();
  if(!item){detail.append(node('p','No requests / Sin solicitudes','muted'));return;}
  detail.append(node('h3',item.customer.name),node('p',item.customer.contact),node('p',states[item.status],'status'),node('p',item.customer.message,'message'));
  if(['queued','failed','blocked'].includes(item.status)) {
    detail.append(action('Generate draft / Generar borrador','/api/draft'));
  }
  const record=item.record;
  if(!record)return;
  const draftActions=node('div','','actions');
  if(item.status==='draft_ready') draftActions.append(action('Regenerate draft / Regenerar borrador','/api/redraft'));
  if(['draft_ready','blocked','approved'].includes(item.status)) {
    const reject=action('Reject draft / Rechazar borrador','/api/reject',{draft_revision:item.draft_revision});reject.className='danger';draftActions.append(reject);
  }
  if(draftActions.children.length)detail.append(draftActions);
  detail.append(node('p',record.fallback_used?'Offline fallback / Respuesta de respaldo sin IA':'AI model / Modelo de IA: '+record.model,record.fallback_used?'status warning':'status'));
  if(record.error_code) detail.append(node('p',record.error_code,'warning'));
  const first=record.language==='es'?'es':'en', second=first==='es'?'en':'es';
  for(const lang of [first,second]) {
    detail.append(node('h3',lang==='es'?'Spanish draft / Borrador en español':'English draft / Borrador en inglés'),node('p',record['draft_'+lang],'draft'));
  }
  const checks=node('ul','');
  for(const check of record.validation) checks.append(node('li',check.level+' · '+check.check));
  detail.append(checks);
  if(item.status==='draft_ready') {
    const radios=node('div','','radio-row');
    for(const lang of ['en','es']) {
      const label=node('label',lang==='es'?'Spanish / Español':'English / Inglés');
      const radio=document.createElement('input');radio.type='radio';radio.name='reply-language';radio.value=lang;radio.checked=lang===first;label.prepend(radio);radios.append(label);
    }
    detail.append(radios);
    const real=document.createElement('input');real.type='checkbox';real.disabled=!live;
    const label=node('label','This is a genuine customer inquiry / Esta es una consulta real de un cliente','check');label.prepend(real);detail.append(label);
    const approve=node('button','Approve draft / Aprobar borrador');approve.type='button';
    approve.onclick=()=>busy(approve,async()=>{
      const language=detail.querySelector('input[name="reply-language"]:checked').value;
      await api('/api/approve',{id:item.id,reviewer,language,real_customer:real.checked,draft_revision:item.draft_revision},true);
      notice('operator-result','Approved; nothing sent / Aprobado; no se ha enviado nada');await load();
    },'operator-result');detail.append(approve);
  }
  if(item.status==='approved') {
    const actions=node('div','','actions');
    const copy=node('button','Copy approved reply / Copiar respuesta aprobada');copy.type='button';
    copy.onclick=()=>busy(copy,async()=>{const epoch=session;await navigator.clipboard.writeText(record['draft_'+item.reviewed_language]);if(epoch===session)notice('operator-result','Copied; not sent / Copiada; no enviada');},'operator-result');
    const sent=node('button','Record manual send / Registrar envío manual');sent.type='button';
    sent.onclick=()=>busy(sent,async()=>{
      if(!confirm('Have you actually sent the approved reply yourself? / ¿Ya envió personalmente la respuesta aprobada?'))return;
      await api('/api/sent',{id:item.id,reviewer,sent_manually:true,draft_revision:item.draft_revision},true);notice('operator-result','Manual send recorded / Envío manual registrado');await load();
    },'operator-result');actions.append(copy,sent);detail.append(actions);
  }
}
// --- Chat with Mrs. Claus ---------------------------------------------------
// The server keeps its own bounded, per-session running context, looked up
// by this page-load's session key. Nothing about the visitor's conversation
// is written to browser storage: a reload starts a fresh chat, the same
// no-persistent-storage policy this file already holds for the operator
// token. The session key itself is never sent back as trusted history -
// each turn is a plain {session_key, message} request.
let chatSessionKey='', chatLog=[], chatBusy=false;
function renderChat() {
  const thread=$('chat-thread'); thread.replaceChildren();
  for(const turn of chatLog) thread.append(node('p',turn.text,'chat-bubble chat-'+turn.role));
  thread.scrollTop=thread.scrollHeight;
  syncTranscriptField();
}
function syncTranscriptField() {
  try {
    const field=document.querySelector('#inquiry-form [name="message"]');
    if(!field) return;
    field.value=chatLog.map(t=>(t.role==='customer'?'Customer / Cliente: ':'Mrs. Claus: ')+t.text).join('\n\n');
  } catch(e) {}
}
function addChatMessage(role,text) { chatLog.push({role,text}); renderChat(); }
function sendChat(text) {
  chatBusy=true; $('chat-send').disabled=true; $('chat-retry').hidden=true;
  notice('chat-status','Mrs. Claus is typing / La Sra. Claus está escribiendo…');
  return api('/api/chat',{session_key:chatSessionKey,message:text}).then(data=>{
    notice('chat-status','');
    addChatMessage('assistant',data.message);
  }).catch(e=>{
    notice('chat-status',e.message||'Connection failed; you can try again or call Santa / Falló la conexión; puede intentar de nuevo o llamar a Santa',true);
    $('chat-retry').hidden=false;
    $('chat-retry').onclick=()=>sendChat(text);
  }).finally(()=>{ chatBusy=false; $('chat-send').disabled=false; });
}
function initChat() {
  if(!$('chat-form')) return;
  chatSessionKey=crypto.randomUUID();
  addChatMessage('assistant',"Hi! I'm Mrs. Claus, a virtual AI assistant at Miami Papa Noel's North Pole workshop. Tell me a bit about the visit you have in mind - the date, the type of event, and the city. / ¡Hola! Soy la Sra. Claus, una asistente virtual de inteligencia artificial en el taller del Polo Norte de Miami Papa Noel. Cuénteme sobre la visita que tiene en mente: la fecha, el tipo de evento y la ciudad.");
  $('chat-form').addEventListener('submit',e=>{
    e.preventDefault();
    if(chatBusy) return;
    const input=$('chat-input'), text=input.value.trim();
    if(!text) return;
    input.value=''; addChatMessage('customer',text);
    return sendChat(text);
  });
  $('send-to-team').addEventListener('toggle',syncTranscriptField);
}
initChat();
$('inquiry-form').addEventListener('submit',e=>{
  e.preventDefault();const form=e.currentTarget;
  busy(form.querySelector('button'),async()=>{
    const fields=new FormData(form);
    const payload={name:fields.get('name'),contact:fields.get('contact'),message:fields.get('message'),consent:form.elements.consent.checked};
    const current=JSON.stringify(payload);
    if(lastSubmission&&current!==lastSubmission) requestKey=crypto.randomUUID();
    lastSubmission=current;
    const result=await api('/api/inquiry',{...payload,request_key:requestKey});
    notice('intake-result','Request received / Solicitud recibida: '+result.request_id+'. Not a booking confirmation / No es una confirmación de reserva.');
    form.reset();requestKey=crypto.randomUUID();lastSubmission='';
  },'intake-result');
});
$('login').addEventListener('submit',e=>{
  e.preventDefault();const nextToken=$('token').value,nextReviewer=$('reviewer').value.trim();
  resetOperatorSession();token=nextToken;reviewer=nextReviewer;
  busy(e.currentTarget.querySelector('button'),async()=>{await load();$('token').value='';notice('operator-result','');},'operator-result');
});
$('refresh').onclick=e=>busy(e.currentTarget,()=>load(),'operator-result');
$('older').onclick=e=>busy(e.currentTarget,()=>load(true),'operator-result');
$('export').onclick=e=>busy(e.currentTarget,async()=>{await api('/api/export',{reviewer},true);notice('operator-result','Private metadata snapshots exported / Exportadas las instantáneas privadas de metadatos');},'operator-result');
function resetOperatorSession() {
  session++;loadVersion++;
  for(const controller of operatorRequests)controller.abort();
  operatorRequests.clear();
  token='';reviewer='';items=[];selected=null;live=false;nextCursor=null;
  $('desk').hidden=true;$('login').hidden=false;$('token').value='';
  $('count').textContent='';$('older').hidden=true;
  $('detail').replaceChildren();$('queue').replaceChildren();
}
$('logout').onclick=()=>{resetOperatorSession();notice('operator-result','Signed out / Sesión cerrada');};
api('/health').then(data=>{
  $('mode').textContent=data.mode==='demo'?'DEMO · Synthetic requests only / Solo solicitudes de prueba':'Inquiry intake · Not a booking confirmation / Recepción de consultas · No confirma reservas';
  $('mode').classList.toggle('demo',data.mode==='demo');
}).catch(()=>{$('mode').textContent='Service unavailable / Servicio no disponible';$('inquiry-form').querySelector('button').disabled=true;});
