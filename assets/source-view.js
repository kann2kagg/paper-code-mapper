// Add actual PDF page pixels and verified crop coordinates to both reading tracks.
const OriginalUI=D.source_ui;
const originalShots=D.screenshots||{};
const originalPages=Object.keys(D.images||{}).map(Number).sort((a,b)=>a-b);
const originalPageCount=D.screenshot_provenance?.page_count||originalPages.length;
function validShotIds(ids){return [...new Set(ids||[])].filter(id=>originalShots[id]&&D.images[String(originalShots[id].page)]);}
function originalSvg(id,full=false,overlay=false,pageOverride=null){
 const s=originalShots[id],p=pageOverride||(s&&s.page),sz=D.sizes[String(p)],uri=D.images[String(p)];
 if(!sz||!uri)return '';
 const c=!full&&s?s.clip:[0,0,sz[0],sz[1]],r=full&&overlay&&s&&s.page===p?s.clip:null;
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${c[0]} ${c[1]} ${c[2]-c[0]} ${c[3]-c[1]}" role="img" aria-label="${esc(OriginalUI.title+' '+p+' '+(s?.title||''))}"><image width="${sz[0]}" height="${sz[1]}" href="${esc(uri)}"/>${r?`<rect x="${r[0]}" y="${r[1]}" width="${r[2]-r[0]}" height="${r[3]-r[1]}" fill="none" stroke="#235fba" stroke-width="1.8" stroke-dasharray="5 3"/>`:''}</svg>`;
}
function sourceGallery(ids,index=0){
 ids=validShotIds(ids);if(!ids.length)return '';
 index=Math.max(0,Math.min(index,ids.length-1));const id=ids[index],s=originalShots[id],cw=s.clip[2]-s.clip[0],ch=s.clip[3]-s.clip[1];
 // Fit the entire cropped image, never silently cut its caption with CSS.
 const width=Math.min(840,620*cw/ch);
 return `<section class="original-source" data-shot-ids="${esc(ids.join(','))}" data-shot-index="${index}"><div class="original-source-head"><strong>${esc(OriginalUI.title)}</strong><small>${esc(OriginalUI.source)}</small></div>${ids.length>1?`<div class="original-source-tabs" role="group" aria-label="${esc(OriginalUI.title)}">${ids.map((key,i)=>`<button data-original-pick="${i}" class="${i===index?'active':''}" aria-pressed="${i===index}">${i+1}. ${esc(originalShots[key].title)}</button>`).join('')}</div>`:''}<div class="original-source-body"><div class="original-source-meta"><b>${esc(OriginalUI.page)} ${s.page} ${esc(OriginalUI.unit)}</b> &nbsp; ${esc(s.title)}</div><div class="original-shot-frame"><button class="original-shot-button" data-original-open="${esc(id)}" style="width:${width}px" title="${esc(OriginalUI.enlarge)}" aria-label="${esc(OriginalUI.enlarge+' '+s.title)}">${originalSvg(id)}</button></div><div class="original-source-actions"><button class="btn primary" data-original-open="${esc(id)}">${esc(OriginalUI.enlarge)}</button><button class="btn" data-original-open="${esc(id)}" data-original-full="true">${esc(OriginalUI.full)}</button></div><div class="original-source-foot">${esc(OriginalUI.hint)}</div></div></section>`;
}
const oldArgumentRenderWithImages=renderArgumentView;
renderArgumentView=function(){
 oldArgumentRenderWithImages();
 if(!argumentAvailable)return;
 const n=AR.nodes[argumentIndex],e=argumentWork.querySelector('.arg-evidence'),ids=validShotIds((n.references||[]).flatMap(r=>r.shot_ids||[]));
 if(e&&ids.length){
  e.querySelector('h4').textContent=ArgumentUI.evidence+' · '+OriginalUI.title;
  e.insertAdjacentHTML('beforeend',sourceGallery(ids));
  const reason=argumentWork.querySelector('.arg-reason-grid');if(reason)reason.before(e);
 }
};
paperHtml=function(l){
 let h=`<div class="sidetitle">${esc(OriginalUI.righttab)}</div>`;
 if(!l.papers?.length)return h+`<div class="none">${esc(U.noPaper)}</div>`;
 for(const idx of l.papers){const p=D.paperPoints[idx];
  h+=`<section class="paperitem"><small>PDF ${esc(U.page)} ${p.page}</small><h4>${esc(p.section)}</h4><span class="paperstatus">${esc(U.statuses[p.status]||p.status)}</span>${sourceGallery(p.shot_ids||[])}<p>${esc(p.paperSummary)}</p><p><b>${esc(U.relation)} </b>${esc(p.relation)}</p>${p.quote?`<p>${esc(p.quote)}</p>`:''}${link(p.paperUrl,U.paperSource)}</section>`;
 }return h;
};
const contextBeforeOriginals=renderArgumentContext;
renderArgumentContext=function(){
 contextBeforeOriginals();
 if(contextBox.hidden)return;
 const l=D.lessons[current];
 const direct=(l.papers||[]).flatMap(i=>D.paperPoints[i].shot_ids||[]);
 const linked=argumentMatches().flatMap(x=>(x.n.references||[]).flatMap(r=>r.shot_ids||[]));
 const ids=validShotIds([...direct,...linked]);
 if(ids.length)contextBox.insertAdjacentHTML('beforeend',`<div class="source-shortcut"><span>${esc(OriginalUI.source)}</span><button class="btn" data-original-open="${esc(ids[0])}">${esc(OriginalUI.shortcut)}</button></div>`);
};
const originalDialog=document.createElement('dialog');originalDialog.id='paperOriginalViewer';
originalDialog.setAttribute('aria-labelledby','originalViewerTitle');
originalDialog.innerHTML=`<div class="original-viewer-head"><div><h3 id="originalViewerTitle"></h3><p>${esc(OriginalUI.note)}</p></div><button class="btn" data-original-close="true">${esc(OriginalUI.close)} ×</button></div><div class="original-viewer-controls"><label for="originalPageSelect">PDF </label><select id="originalPageSelect" aria-label="PDF page">${Object.keys(D.images).map(Number).sort((a,b)=>a-b).map(p=>`<option value="${p}">${p} / ${originalPageCount}</option>`).join('')}</select><button class="btn" data-original-view="crop" id="originalCropButton">${esc(OriginalUI.crop)}</button><button class="btn" data-original-view="full" id="originalFullButton">${esc(OriginalUI.full)}</button><button class="btn" data-original-zoom="down" aria-label="Zoom out">−</button><span class="zoomread" id="originalZoomRead"></span><button class="btn" data-original-zoom="up" aria-label="Zoom in">+</button><button class="btn" data-original-zoom="fit">${esc(OriginalUI.fit)}</button><label><input type="checkbox" id="originalShowFrame" checked> ${esc(OriginalUI.frame)}</label></div><div class="original-viewer-stage" id="originalViewerStage"><div class="original-viewport" id="originalViewport"></div></div><div class="original-viewer-note" id="originalViewerNote"></div>`;
document.body.append(originalDialog);
let originalState={id:null,page:originalPages[0],mode:'full',zoom:1,overlay:true},originalOpener=null;
function renderOriginalViewer(resetScroll=false){
 const v=originalState,s=originalShots[v.id],sz=D.sizes[String(v.page)],c=s?s.clip:[0,0,...sz];
 const full=v.mode==='full',available=Math.max(220,$('originalViewerStage').clientWidth-(innerWidth<640?18:40));
 const baseWidth=full?Math.min(available,1020):Math.min(available,Math.max(450,Math.min(1120,(c[2]-c[0])*2.8)));
 $('originalViewport').style.width=`${Math.round(baseWidth*v.zoom)}px`;
 $('originalViewport').innerHTML=originalSvg(v.id,full,v.overlay,v.page);
 $('originalViewerTitle').textContent=`${OriginalUI.page} ${v.page} ${OriginalUI.unit} · ${s?s.title:OriginalUI.all}`;
 $('originalPageSelect').value=String(v.page);
 $('originalCropButton').disabled=!s;
 $('originalCropButton').classList.toggle('is-on',!full);
 $('originalFullButton').classList.toggle('is-on',full);
 $('originalShowFrame').disabled=!full||!s;
 $('originalShowFrame').checked=v.overlay;
 $('originalZoomRead').textContent=Math.round(v.zoom*100)+'%';
 $('originalViewerNote').textContent=(full?OriginalUI.fullnote:OriginalUI.note)+' '+OriginalUI.pagenote;
 if(resetScroll){$('originalViewerStage').scrollTop=0;$('originalViewerStage').scrollLeft=0;}
}
function openOriginal(id=null,full=false,opener=null,page=originalPages[0]){
 const s=originalShots[id];if(!s&&!D.images[String(page)])return;
 originalOpener=opener||document.activeElement;
 originalState={id:s?id:null,page:s?s.page:page,mode:full||!s?'full':'crop',zoom:1,overlay:true};
 if(!originalDialog.open)originalDialog.showModal();
 renderOriginalViewer(true);
}
const fullButton=document.createElement('button');fullButton.className='btn';fullButton.id='paperFullButton';fullButton.textContent=OriginalUI.all;
fullButton.onclick=e=>openOriginal(null,true,e.currentTarget,originalPages[0]);modeBar.append(fullButton);
$('originalPageSelect').addEventListener('change',e=>{const p=Number(e.target.value);originalState={id:null,page:p,mode:'full',zoom:1,overlay:true};renderOriginalViewer(true);});
$('originalShowFrame').addEventListener('change',e=>{originalState.overlay=e.target.checked;renderOriginalViewer();});
originalDialog.addEventListener('close',()=>{if(originalOpener?.isConnected)originalOpener.focus({preventScroll:true});});
window.addEventListener('resize',()=>{if(originalDialog.open)renderOriginalViewer();});
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.originalPick!==undefined){const gallery=b.closest('.original-source');gallery.outerHTML=sourceGallery(gallery.dataset.shotIds.split(','),Number(b.dataset.originalPick));}
 if(b.dataset.originalOpen){openOriginal(b.dataset.originalOpen,!!b.dataset.originalFull,b);}
 if(b.dataset.originalClose)originalDialog.close();
 if(b.dataset.originalView){if(b.dataset.originalView==='crop'&&!originalState.id)return;originalState.mode=b.dataset.originalView;originalState.zoom=1;renderOriginalViewer(true);}
 if(b.dataset.originalZoom){let z=originalState.zoom;z=b.dataset.originalZoom==='fit'?1:b.dataset.originalZoom==='up'?z*1.25:z/1.25;originalState.zoom=Math.min(4,Math.max(.5,z));renderOriginalViewer();}
});
U.paper=OriginalUI.righttab;document.querySelector('[data-tab="paper"]').textContent=OriginalUI.righttab;
$('about').insertAdjacentHTML('beforeend',`<p><strong>${esc(OriginalUI.title)}:</strong> ${esc(OriginalUI.note)} ${esc(OriginalUI.pagenote)}</p>`);
renderSide();renderArgumentContext();if(readerView==='argument')renderArgumentView();
