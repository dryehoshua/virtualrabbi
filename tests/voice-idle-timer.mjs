import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const app=fs.readFileSync('web/app.js','utf8');
const timer=app.slice(app.indexOf('function startPublicTimer(seconds)'),app.indexOf("window.addEventListener('pagehide'"));
const label={textContent:''};let heartbeat, reply, stopped=0;const notices=[];
const context=vm.createContext({publicCallId:'first',publicHeartbeat:null,publicClock:null,
 $:()=>label,element:()=>label,english:()=>true,
 clearInterval(){},setInterval(fn){heartbeat=fn;return 1;},
 request:async()=>reply,stopCall(){stopped++;},toast:t=>notices.push(t),RabbiLocale:{t:k=>k}});
vm.runInContext(timer+';startPublicTimer(1800)',context);
assert.match(label.textContent,/30:00/);
reply={status:'active',seconds:1800,active:false};
for(let i=0;i<180;i++)await heartbeat(); // Fifteen minutes of five-second heartbeats.
assert.match(label.textContent,/30:00/);
assert.equal(stopped,0);
reply={status:'active',seconds:1790,active:true};await heartbeat();
assert.match(label.textContent,/29:50/);
reply={status:'closed',seconds:1790,active:false,reason:'idle'};await heartbeat();
assert.equal(stopped,1);assert.match(notices[0],/remaining time is saved/);
let resolve;
context.request=()=>new Promise(r=>resolve=r);
const pending=heartbeat();context.publicCallId='new-call';
resolve({status:'closed',seconds:0,reason:'time'});await pending;
assert.equal(stopped,1,'a late heartbeat must not end a new call');
console.log('Public timer: idle credit, server time, idle closure and stale heartbeat passed.');
