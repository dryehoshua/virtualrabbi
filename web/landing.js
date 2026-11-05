'use strict';
let language=localStorage.getItem('rabbi.landingLanguage')||'es',links={};
const $=id=>document.getElementById(id);
function render(){document.documentElement.lang=language;$('language').value=language;document.querySelectorAll('[data-es]').forEach(el=>{el.innerHTML=el.dataset[language]});$('amounts').replaceChildren();for(const amount of ['5','18','52','100','260','450','1800','other']){const item=document.createElement(links[amount]?'a':'span');item.textContent=amount==='other'?(language==='en'?'Other amount':'Otro importe'):'US$'+Number(amount).toLocaleString('en-US');if(links[amount]){item.href=links[amount];item.target='_blank';item.rel='noopener noreferrer'}$('amounts').append(item)}$('supportPending').hidden=Object.keys(links).length>0}
$('language').onchange=e=>{language=e.target.value;localStorage.setItem('rabbi.landingLanguage',language);render()};
$('loginOpen').onclick=()=>$('loginDialog').showModal();$('closeLogin').onclick=()=>$('loginDialog').close();
$('loginForm').onsubmit=async e=>{e.preventDefault();const button=e.target.querySelector('button');button.disabled=true;$('loginError').textContent='';try{const fields=new FormData(e.target);const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:fields.get('email'),password:fields.get('password')})});const data=await r.json();if(!r.ok)throw new Error(data.error);e.target.reset();location.href='/study'}catch(err){$('loginError').textContent=err.message}finally{button.disabled=false}};
$('logout').onclick=async()=>{await fetch('/api/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});location.reload()};
render();fetch('/api/status').then(r=>r.json()).then(s=>{links=s.support_links||{};render()}).catch(()=>{});
fetch('/api/me').then(r=>r.json()).then(me=>{if(me.email){$('loginOpen').hidden=true;$('logout').hidden=false}}).catch(()=>{});
