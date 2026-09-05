// Parallel research-argument view. Never executes inspected repository code.
const ArgumentUI = D.argument_ui || ((D.language === 'en') ? {
 code:'Read the code', logic:'Author argument', hint:'Execution order and research reasoning are different tracks.',
 title:'Understand the author argument', intro:'Keep the research problem, proposed explanation, method, evidence and limits together.',
 back:'Return to current code', nav:'Reasoning nodes. Branches below are argument relations, not function calls.',
 question:'Question at this step', because:'Why this step follows', consequence:'What it motivates next',
 evidence:'Paper evidence', boundary:'What this does not establish', links:'Code connected to this claim',
 edges:'Connections in the author argument', source:'Open paper location', prev:'Previous reading node', next:'Next reading node',
 context:'Research context of this code', overview:'Full author argument',
 noArgument:'No supported author argument is available. Do not invent one from the code.',
 noLocal:'No direct research claim is linked to this block. Engineering context and code explanation remain separate.',
 bases:{'author-stated':'Author statement','source-analysis':'Source-based interpretation','teaching':'Teaching only'},
 roles:{implements:'Implementation',configures:'Configuration',measures:'Measurement',infrastructure:'Engineering support'},
 block:'Code block', earlier:'Earlier node', later:'Related node', position:'Teaching sequence, not causal proof'
} : {
 code:'代码逐条解析',logic:'作者论证主线',hint:'代码回答“怎么做”，论证主线回答“为什么这样做”。',
 title:'看清作者是怎样推到这个方法的',intro:'不是把章节摘要串起来，而是保留问题、原因解释、设计选择、实验依据和适用边界之间的关系。',
 back:'回到刚才的代码',nav:'沿作者的论证阅读；存在分支与依赖，不是程序调用顺序。',
 question:'这个环节在回答什么',because:'为什么会走到这一步',consequence:'这一点又引出什么',
 evidence:'论文中的依据',boundary:'不能由此推出什么',links:'哪些代码承担了这一环节',
 edges:'放回整条论证中看',source:'定位到论文',prev:'上一个阅读环节',next:'下一个阅读环节',
 context:'这段代码在研究逻辑中的位置',overview:'看完整作者逻辑',
 noArgument:'目前没有可核对的完整作者论证。不能只凭代码反推出作者想法。',
 noLocal:'这块代码没有被直接绑定到研究命题。工程支撑仍按执行逻辑解释，不强行配一条论文结论。',
 bases:{'author-stated':'作者明确论述','source-analysis':'据原文整理的解释','teaching':'独立教学示意'},
 roles:{implements:'实现方法',configures:'选择实验配置',measures:'计算评估指标',infrastructure:'工程支撑'},
 block:'代码块',earlier:'前置论点',later:'关联论点',position:'阅读顺序不等于严格因果证明'
});
const AR=D.argument, argumentAvailable=AR?.status==='provided'&&AR.nodes?.length;
let argumentIndex=argumentAvailable?Math.max(0,AR.nodes.findIndex(n=>n.id===AR.default_node)):0;
let readerView='code';
const codeApp=document.querySelector('.app');
const modeBar=document.createElement('div');modeBar.className='modebar';modeBar.setAttribute('role','toolbar');
modeBar.innerHTML=`<button class="btn active" id="modeCode" aria-pressed="true">${esc(ArgumentUI.code)}</button><button class="btn" id="modeArgument" aria-pressed="false">${esc(ArgumentUI.logic)}</button><span class="modehint">${esc(ArgumentUI.hint)}</span>`;
codeApp.before(modeBar);
const argumentWork=document.createElement('section');argumentWork.className='argument-work';argumentWork.id='argumentWork';argumentWork.hidden=true;codeApp.after(argumentWork);
const contextBox=document.createElement('div');contextBox.className='argument-context';contextBox.id='argumentContext';
$('intro').after(contextBox);
function argumentBasis(b){return ArgumentUI.bases[b]||b||''}
function argumentMatches(){if(!argumentAvailable)return [];const l=D.lessons[current];return AR.nodes.flatMap((n,ni)=>(n.code_links||[]).filter(c=>c.lesson===l.id&&(c.block==null||c.block===stage||all)).map(c=>({n,ni,c})));}
function renderArgumentContext(){
 if(!argumentAvailable){contextBox.hidden=true;return}contextBox.hidden=false;
 const hits=argumentMatches();contextBox.innerHTML=`<div class="context-head"><strong>${esc(ArgumentUI.context)}</strong><button class="btn" data-open-argument="${hits[0]?.ni??argumentIndex}">${esc(ArgumentUI.overview)}</button></div>`+
 (hits.length?hits.map(({n,ni,c})=>`<div class="context-entry"><button data-open-argument="${ni}">${esc(ArgumentUI.roles[c.role])} · ${esc(n.title)}</button><p>${esc(c.explanation)}</p></div>`).join(''):`<div class="context-empty">${esc(ArgumentUI.noLocal)}</div>`);
}
function switchReaderView(mode){readerView=mode;document.body.classList.toggle('argument-active',mode==='argument');codeApp.hidden=mode!=='code';argumentWork.hidden=mode!=='argument';$('modeCode').classList.toggle('active',mode==='code');$('modeArgument').classList.toggle('active',mode==='argument');$('modeCode').setAttribute('aria-pressed',String(mode==='code'));$('modeArgument').setAttribute('aria-pressed',String(mode==='argument'));}
function showCodeView(push=true){switchReaderView('code');renderArgumentContext();if(push)history.replaceState(null,'','#'+D.lessons[current].id);}
function showArgumentView(index=argumentIndex,push=true){
 switchReaderView('argument');
 if(!argumentAvailable){argumentWork.innerHTML=`<h2>${esc(ArgumentUI.logic)}</h2><p class="arg-note-empty">${esc(AR?.reason||ArgumentUI.noArgument)}</p>`;return;}
 argumentIndex=Math.max(0,Math.min(Number(index)||0,AR.nodes.length-1));renderArgumentView();if(push)history.replaceState(null,'','#logic='+AR.nodes[argumentIndex].id);
}
function argumentLinkHTML(c){
 const li=D.lessons.findIndex(l=>l.id===c.lesson);if(li<0)return '';const l=D.lessons[li],b=c.block==null?null:l.blocks[c.block];
 return `<button class="arg-code-link" data-argument-lesson="${li}" data-argument-block="${c.block??0}"><span class="arg-role">${esc(ArgumentUI.roles[c.role])}</span><span class="arg-file">${esc(b?.path||l.file)}${b?.symbol?' · '+esc(b.symbol):''}</span><strong>${esc(b?.title||l.title)}</strong><p>${esc(c.explanation)}</p></button>`;
}
function renderArgumentView(){
 const n=AR.nodes[argumentIndex];
 const edges=(AR.edges||[]).filter(e=>e.from===n.id||e.to===n.id).map(e=>{
  const outgoing=e.from===n.id,targetId=outgoing?e.to:e.from,ti=AR.nodes.findIndex(z=>z.id===targetId),target=AR.nodes[ti];if(!target)return '';
  return `<div class="arg-edge"><span>${esc(outgoing?ArgumentUI.later:ArgumentUI.earlier)} · ${esc(e.relation)} </span><button data-open-argument="${ti}">${esc(target.title)}</button><em>${esc(argumentBasis(e.basis))}</em><p>${esc(e.explanation)}</p></div>`;
 }).join('');
 argumentWork.innerHTML=`<div class="arg-top"><div><h2>${esc(AR.title||ArgumentUI.title)}</h2><p>${esc(ArgumentUI.intro)}</p></div><button class="btn" data-return-code="true">${esc(ArgumentUI.back)}</button></div><div class="arg-intro"><strong>${esc(AR.question)}</strong><p>${esc(AR.takeaway)}</p><p class="arg-scope">${esc(AR.scope)}</p></div><div class="arg-grid"><nav class="arg-nav" aria-label="${esc(ArgumentUI.logic)}"><div class="arg-nav-caption">${esc(ArgumentUI.nav)}</div>${AR.nodes.map((a,i)=>`<button class="arg-node ${i===argumentIndex?'active':''}" data-open-argument="${i}" ${i===argumentIndex?'aria-current="step"':''}><span class="arg-index">${String(i+1).padStart(2,'0')}</span><span><small>${esc(a.stage)}</small>${esc(a.title)}</span></button>`).join('')}</nav><div><article class="arg-detail"><div class="arg-detail-head"><span class="arg-badge">${esc(argumentBasis(n.basis))}</span><span class="arg-stage">${argumentIndex+1} / ${AR.nodes.length} · ${esc(n.stage)}</span><h3 tabindex="-1" id="argumentNodeHeading">${esc(n.title)}</h3></div><div class="arg-detail-body"><div class="arg-question">${esc(ArgumentUI.question)}：${esc(n.question)}</div><p class="arg-claim">${esc(n.claim)}</p><div class="arg-reason-grid"><div class="arg-reason"><h4>${esc(ArgumentUI.because)}</h4><p>${esc(n.because)}</p></div><div class="arg-reason"><h4>${esc(ArgumentUI.consequence)}</h4><p>${esc(n.consequence)}</p></div></div><div class="arg-evidence"><h4>${esc(ArgumentUI.evidence)}</h4>${(n.references||[]).map(r=>`<div class="arg-ref"><strong>PDF ${r.page} · ${esc(r.section)}</strong><span>${esc(r.locator)}</span>${link(r.url,ArgumentUI.source)}</div>`).join('')}</div><div class="arg-boundary"><b>${esc(ArgumentUI.boundary)}</b>${esc(n.boundary)}</div><div class="arg-links"><h4>${esc(ArgumentUI.links)}</h4>${n.code_links?.length?n.code_links.map(argumentLinkHTML).join(''):`<p class="arg-nocode">${esc(n.code_note||'')}</p>`}</div>${edges?`<div class="arg-edges"><h4>${esc(ArgumentUI.edges)}</h4>${edges}</div>`:''}</div></article><div class="arg-pager"><button class="btn" data-open-argument="${Math.max(0,argumentIndex-1)}" ${argumentIndex===0?'disabled':''}>← ${esc(ArgumentUI.prev)}</button><button class="btn" data-open-argument="${Math.min(AR.nodes.length-1,argumentIndex+1)}" ${argumentIndex===AR.nodes.length-1?'disabled':''}>${esc(ArgumentUI.next)} →</button></div><p class="arg-scope">${esc(ArgumentUI.position)}</p></div></div>`;
 if(window.innerWidth<=640){const nav=argumentWork.querySelector('.arg-nav'),active=nav.querySelector('.arg-node.active');if(active)nav.scrollLeft=Math.max(0,active.offsetLeft-nav.offsetLeft-(nav.clientWidth-active.clientWidth)/2);}
}
const selectBeforeArgument=select;
select=function(n,push=true){selectBeforeArgument(n,push);showCodeView(false);};
const renderCodeBeforeArgument=renderCode;
renderCode=function(){renderCodeBeforeArgument();renderArgumentContext();};
$('modeCode').onclick=()=>showCodeView();$('modeArgument').onclick=()=>showArgumentView();
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.openArgument!==undefined){showArgumentView(Number(b.dataset.openArgument));$('argumentNodeHeading')?.focus({preventScroll:true});}
 if(b.dataset.returnCode)showCodeView();
 if(b.dataset.argumentLesson!==undefined){select(Number(b.dataset.argumentLesson));stage=Number(b.dataset.argumentBlock)||0;all=false;renderCode();renderArgumentContext();showCodeView();$('title')?.scrollIntoView({block:'start'});}
});
window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#logic=')){const i=AR?.nodes?.findIndex(n=>n.id===location.hash.slice(7));if(i>=0)showArgumentView(i,false)}else{const i=D.lessons.findIndex(l=>l.id===location.hash.slice(1));if(i>=0){if(i!==current)select(i,false);showCodeView(false)}}});
renderArgumentContext();
if(location.hash.startsWith('#logic=')&&argumentAvailable){const i=AR.nodes.findIndex(n=>n.id===location.hash.slice(7));showArgumentView(Math.max(0,i),false);}else if(!location.hash&&D.default_view==='argument')showArgumentView(argumentIndex,false);
