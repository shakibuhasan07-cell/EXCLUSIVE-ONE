function toggleMenu(){const m=document.getElementById('userMenu');if(m)m.classList.toggle('open')}
document.addEventListener('click',e=>{const m=document.getElementById('userMenu');if(m&&!e.target.closest('.nav-user'))m.classList.remove('open')})
function stepQty(btn,delta){const input=btn.parentElement.querySelector('input');input.value=Math.max(0,(parseInt(input.value)||0)+delta)}
function showPayment(name){const box=document.getElementById('paymentHelp');if(!box)return;const info={"bKash":"Send money to bKash: 01609228262","Nagad":"Send money to Nagad: 01609228262","Rocket":"Send money to Rocket: 01632211644","Bank Card":"Use your bank/card gateway. Never share CVV in chat.","Cash on Delivery":"Pay when the order arrives."};box.textContent=info[name]||''}

document.addEventListener("DOMContentLoaded",()=>{const r=document.querySelector("input[name=payment]:checked");if(r)showPayment(r.value)})

window.addEventListener('load',()=>{const l=document.getElementById('pageLoader');if(l)setTimeout(()=>l.classList.add('hide'),180)});
document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a||a.target==='_blank'||a.href.startsWith('javascript:')||a.getAttribute('href')?.startsWith('#'))return;try{const u=new URL(a.href);if(u.origin===location.origin&&a.getAttribute('href')!=='#'){const l=document.getElementById('pageLoader');if(l){l.classList.remove('hide');setTimeout(()=>l.classList.add('hide'),1800)}}}catch(_){} });
function applyPromo(){const i=document.querySelector('input[name=coupon]');if(i){i.focus();i.value=i.value.trim().toUpperCase()||'WELCOME10';}}
function recalcCheckout(){const d=document.getElementById('district');if(d){const note=document.querySelector('.delivery-note span');if(note)note.innerHTML=(d.value==='Dhaka'?'Inside Dhaka ৳60':'Outside Dhaka ৳120')+' • <strong>৳2,999+ FREE</strong>';}}
(function(){const s=document.querySelector('.product-slider');if(!s||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;let timer=setInterval(()=>{if(s.scrollWidth<=s.clientWidth)return;const max=s.scrollWidth-s.clientWidth;s.scrollTo({left:s.scrollLeft>=max-8?0:s.scrollLeft+Math.min(s.clientWidth*.78,360),behavior:'smooth'});},3600);s.addEventListener('pointerdown',()=>clearInterval(timer),{once:true});})();
