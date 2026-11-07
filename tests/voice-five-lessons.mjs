// Exercise the production controller through all five real lessons, including retries.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const language=process.env.STUDY_LANGUAGE||'es';
const batches=process.env.STUDY_BATCH==='all'?['01','02']:[process.env.STUDY_BATCH||'01'];
const units=batches.flatMap(batch=>JSON.parse(fs.readFileSync('Estudio/jaye-sara/08-lecciones-'+batch+'.json','utf8')));
const nodes=new Map();
const node=()=>({style:{},classList:{add(){},remove(){},toggle(){}},append(){},replaceChildren(){},querySelector(){return node();}});
const document={getElementById(id){if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);},querySelector(){return node();},querySelectorAll(){return[];},createElement:node};
const sent=[];
const context=vm.createContext({console,document,window:{scrollTo(){}},URL,crypto:globalThis.crypto,Map,JSON,Promise,setTimeout,clearTimeout,setInterval,clearInterval,sent,units,language});
const source=fs.readFileSync('web/app.js','utf8').split("$('parashaSelect').onchange=")[0];
vm.runInContext(source,context);
await vm.runInContext(`
doc={id:'test',study_language:language,units,current_unit:0,completed:[],location:units[0].location.start,cursor:{unit_id:units[0].id,phase:'hebrew'}};
renderStudy=()=>{};renderUnit=()=>{};renderLocation=()=>{};
request=async(path,data)=>{
 if(path==='/api/cursor'){doc.cursor={unit_id:data.unit_id,phase:data.phase,interrupted:data.interrupted};return doc;}
 if(path==='/api/call-context')return{instructions:'Torah Or'};
 if(path==='/api/progress'){
  if(data.complete&&!doc.completed.includes(unit().id))doc.completed.push(unit().id);
  doc.current_unit=data.current_unit;
  if(doc.cursor.unit_id!==units[data.current_unit].id){doc.cursor={unit_id:units[data.current_unit].id,phase:'hebrew'};doc.location=units[data.current_unit].location.start;}
  return doc;
 }
 throw Error('Unexpected request '+path);
};
connected=true;callGeneration=1;channel={readyState:'open',send(raw){sent.push(JSON.parse(raw));}};
resumeGuided();`,context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
await flush();
let counter=0,injected=false;
const readings=new Map();
const event=async e=>{context.event=e;await vm.runInContext('handleCallEvent(event,1)',context);await flush();};
while(vm.runInContext('autoStudy',context)&&counter<300){
 const before=sent.filter(e=>e.type==='response.create').length;
 const phase=vm.runInContext('doc.cursor.phase',context);
 const unitId=vm.runInContext('unit().id',context);
 const chunk=vm.runInContext("phaseChunks[phaseChunkIndex]||'Explicación breve'",context);
 const id='response-'+(++counter);
 await event({type:'response.created',response:{id}});
 // One incomplete output must retry the same fragment, only after playback ends.
 if(!injected&&phase==='translation'){
  injected=true;
  await event({type:'response.done',response:{id,status:'incomplete',status_details:{reason:'max_output_tokens'},output:[{content:[{type:'audio',transcript:'Partial response'}]}]}});
  assert.equal(sent.filter(e=>e.type==='response.create').length,before);
  await event({type:'output_audio_buffer.stopped',response_id:id});
  assert.equal(vm.runInContext('unit().id',context),unitId);
  assert.equal(vm.runInContext('doc.cursor.phase',context),phase);
  assert.equal(vm.runInContext('phaseChunks[phaseChunkIndex]',context),chunk);
  assert.equal(sent.filter(e=>e.type==='response.create').length,before+1);
  continue;
 }
 if(['hebrew','translation'].includes(phase)){
  const key=unitId+':'+phase;readings.set(key,[...(readings.get(key)||[]),chunk]);
 }
 // Alternate event order: audio may finish before or after generation metadata arrives.
 if(counter%2)await event({type:'output_audio_buffer.stopped',response_id:id});
 await event({type:'response.done',response:{id,status:'completed',output:[{content:[{type:'audio',transcript:chunk}]}]}});
 if(!(counter%2))await event({type:'output_audio_buffer.stopped',response_id:id});
 const after=sent.filter(e=>e.type==='response.create').length;
 await event({type:'output_audio_buffer.stopped',response_id:id});
 assert.equal(sent.filter(e=>e.type==='response.create').length,after,'duplicate playback event must not skip content');
}
assert(counter<300,'five lessons must complete without an unbounded loop');
assert.equal(vm.runInContext('unitIndex',context),units.length-1);
assert.equal(vm.runInContext('doc.completed.length',context),units.length);
assert.equal(vm.runInContext('lessonFlow',context),false);
const normalized=s=>s.replace(/\s+/g,'');
for(const u of units)for(const [phase,field] of [['hebrew','hebrew'],['translation',language==='en'?'translation_en':'translation']]){
 assert.equal(normalized(readings.get(u.id+':'+phase).join(' ')),normalized(u[field]),'all source words must be read in order');
}
assert(!sent.some(e=>e.type==='response.create'&&e.response.metadata.lesson_phase==='pause'),'no artificial section-end question');
// A generation with no audio must retry without waiting forever for a playback event.
await vm.runInContext("unitIndex=0;doc.cursor={unit_id:units[0].id,phase:'hebrew'};lessonFlow=true;autoStudy=true;speakPhase('hebrew')",context);
await event({type:'response.created',response:{id:'empty'}});
await event({type:'response.done',response:{id:'empty',status:'completed',output:[]}});
assert.equal(vm.runInContext('phaseRetries',context),1);
await event({type:'response.created',response:{id:'empty-again'}});
await event({type:'response.done',response:{id:'empty-again',status:'completed',output:[]}});
assert.equal(vm.runInContext('autoStudy',context),false,'persistent failure must stop safely, not consume forever');
// A pause while the bookmark is saving must prevent a late response.create.
await vm.runInContext(`(async()=>{
lessonFlow=true;autoStudy=true;const oldRequest=request;
let resolveCheckpoint;request=async(path,data)=>path==='/api/cursor'?new Promise(r=>{resolveCheckpoint=()=>r(doc);}):oldRequest(path,data);
const preparing=speakPhase('hebrew');
readingEpoch++;lessonFlow=false;autoStudy=false;
resolveCheckpoint();await preparing;
})()`,context);
assert.equal(vm.runInContext('pendingPhase',context),false);
clearTimeout(vm.runInContext('toastTimer',context));
console.log(units.length+' Chayei Sarah lessons ('+language+'): complete readings, transitions, recovery, pause and end-of-installment checks passed.');
