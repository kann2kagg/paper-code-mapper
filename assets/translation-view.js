// Translation data are authored against actual source crops, not inferred from analysis.
const ZH=D.screenshot_translations||{},TUI=D.translation_ui;
function translatedTitle(id){return ZH[id]?.title_target||ZH[id]?.title_zh||originalShots[id]?.title||'';}
function equationHTML(text){return esc(text).replace(/_\{([^{}]+)\}/g,'<sub>$1</sub>').replace(/\^\{([^{}]+)\}/g,'<sup>$1</sup>');}
function translatedBlocks(id){
 const t=ZH[id];if(!t||t.status==='unavailable')return `<p class="translation-scope">${esc(TUI.noTranslation)} ${esc(t?.reason||'')}</p>`;
 let h=`<h4>${esc(t.title_target||t.title_zh)}</h4>`;
 for(const b of t.blocks){
  if(b.type==='paragraph')h+=`<p>${esc(b.text)}</p>`;
  else if(b.type==='heading')h+=`<h5>${esc(b.text)}</h5>`;
  else if(b.type==='equation')h+=`<div class="translation-equation" role="math">${equationHTML(b.text)}</div>`;
  else if(b.type==='code')h+=`<pre class="translation-code">${esc(b.text)}</pre>`;
  else if(b.type==='pairs')h+=`<h5>${esc(b.title)}</h5><div class="translation-table-wrap"><table class="translation-table pairs"><thead><tr><th>${esc(TUI.english)}</th><th>${esc(TUI.chinese)}</th></tr></thead><tbody>${b.rows.map(r=>`<tr>${r.map(c=>`<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  else if(b.type==='table')h+=`<div class="translation-table-wrap" tabindex="0" aria-label="${esc(TUI.tableHint)}"><table class="translation-table ${b.variant==='prose'?'prose':b.headers.length>4?'numerical':''}"><thead><tr>${b.headers.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(r=>`<tr>${r.map(c=>`<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 }
 if(t.notes?.length)h+=`<div class="translation-notes"><strong>${esc(TUI.notes)}</strong>${t.notes.map(x=>`<div>${esc(x)}</div>`).join('')}</div>`;
 if(t.related_ids?.length)h+=`<div class="translation-links">${t.related_ids.map(x=>`<button class="btn" data-trans-link="${esc(x)}">${esc(TUI.continued)} ${esc(translatedTitle(x))}</button>`).join('')}</div>`;
 return h;
}
function translationBox(id){return `<details class="translation-box" data-translation-id="${esc(id)}" open><summary>${esc(TUI.heading)}<small>${esc(TUI.badge)}</small></summary><div class="translation-content">${translatedBlocks(id)}</div></details>`;}
sourceGallery=function(ids,index=0){
 ids=validShotIds(ids);if(!ids.length)return '';
 index=Math.max(0,Math.min(index,ids.length-1));const id=ids[index],s=originalShots[id],cw=s.clip[2]-s.clip[0],ch=s.clip[3]-s.clip[1],width=Math.min(840,620*cw/ch);
 return `<section class="original-source" data-shot-ids="${esc(ids.join(','))}" data-shot-index="${index}"><div class="original-source-head"><strong>${esc(TUI.sourceHeading)}</strong><small>${esc(OriginalUI.source)}</small></div>${ids.length>1?`<div class="original-source-tabs" role="group" aria-label="${esc(OriginalUI.title)}">${ids.map((key,i)=>`<button data-original-pick="${i}" class="${i===index?'active':''}" aria-pressed="${i===index}">${i+1}. ${esc(translatedTitle(key))}</button>`).join('')}</div>`:''}<div class="original-source-body"><div class="original-source-meta"><b>${esc(OriginalUI.page)} ${s.page} ${esc(OriginalUI.unit)}</b> &nbsp; ${esc(translatedTitle(id))}<span class="bilingual-shot-title">${esc(s.title)}</span></div><div class="original-shot-frame"><button class="original-shot-button" data-original-open="${esc(id)}" style="width:${width}px" title="${esc(TUI.enlarge)}" aria-label="${esc(TUI.enlarge+' '+translatedTitle(id))}">${originalSvg(id)}</button></div><div class="original-source-actions"><button class="btn primary" data-original-open="${esc(id)}">${esc(TUI.enlarge)}</button><button class="btn" data-original-open="${esc(id)}" data-original-full="true">${esc(OriginalUI.full)}</button></div>${translationBox(id)}<div class="original-source-foot">${esc(TUI.galleryHint)}</div></div></section>`;
};
const bilingualStage=document.createElement('div');bilingualStage.className='original-bilingual-stage';bilingualStage.id='originalBilingualStage';
$('originalViewerStage').before(bilingualStage);bilingualStage.append($('originalViewerStage'));
const translationPane=document.createElement('aside');translationPane.className='original-translation-pane';translationPane.id='originalTranslationPane';translationPane.setAttribute('aria-label',TUI.heading);bilingualStage.append(translationPane);
const zhToggle=document.createElement('button');zhToggle.className='btn is-on';zhToggle.id='originalZhToggle';zhToggle.textContent=TUI.hide;zhToggle.setAttribute('aria-pressed','true');originalDialog.querySelector('.original-viewer-controls').append(zhToggle);
let zhVisible=true,translationViewerKey=null;
const renderOriginalWithoutZh=renderOriginalViewer;
renderOriginalViewer=function(resetScroll=false){
 const v=originalState,s=originalShots[v.id],key=`${v.page}|${v.id||''}`;
 if(key!==translationViewerKey){
  translationViewerKey=key;
  if(s){
   translationPane.innerHTML=`<div class="translation-pane-caption">${esc(TUI.heading)} &middot; PDF ${v.page} &middot; ${esc(TUI.badge)}</div><p class="translation-scope" id="translationViewerScope"></p><div class="translation-content">${translatedBlocks(v.id)}</div>`;
  }else{
   const ids=Object.keys(originalShots).filter(id=>originalShots[id].page===v.page);
   translationPane.innerHTML=`<div class="translation-pane-caption">${esc(TUI.heading)} &middot; PDF ${v.page}</div><p class="translation-scope">${esc(TUI.pageScope)}</p>${ids.length?`<div class="translation-page-list">${ids.map(id=>`<button class="btn" data-trans-onpage="${esc(id)}">${esc(translatedTitle(id))}</button>`).join('')}</div>`:`<p class="translation-scope">${esc(TUI.noPage)}</p>`}`;
  }
  translationPane.scrollTop=0;
 }
 if($('translationViewerScope'))$('translationViewerScope').textContent=v.mode==='full'?TUI.fullScope:TUI.cropScope;
 renderOriginalWithoutZh(resetScroll);
 $('originalViewerTitle').textContent=`PDF ${v.page} / ${originalPageCount} · ${s?translatedTitle(v.id):OriginalUI.all}`;
 $('originalViewerNote').textContent=TUI.viewerNote;
};
zhToggle.onclick=()=>{zhVisible=!zhVisible;bilingualStage.classList.toggle('translation-off',!zhVisible);zhToggle.classList.toggle('is-on',zhVisible);zhToggle.setAttribute('aria-pressed',String(zhVisible));zhToggle.textContent=zhVisible?TUI.hide:TUI.show;renderOriginalViewer();};
const translationIndex=document.createElement('dialog');translationIndex.id='translationIndex';translationIndex.setAttribute('aria-labelledby','translationIndexTitle');
const indexPages=[...new Set(Object.values(originalShots).map(s=>s.page))].sort((a,b)=>a-b);
translationIndex.innerHTML=`<button class="btn close" data-translation-close="true">${esc(OriginalUI.close)}</button><h3 id="translationIndexTitle">${esc(TUI.index)}</h3><p class="translation-index-intro">${esc(TUI.indexIntro)}</p>${indexPages.map(p=>`<section class="translation-index-group"><h4>PDF ${p}</h4><div class="translation-index-links">${Object.keys(originalShots).filter(id=>originalShots[id].page===p).map(id=>`<button class="btn" data-trans-index="${esc(id)}">${esc(translatedTitle(id))}</button>`).join('')}</div></section>`).join('')}`;
document.body.append(translationIndex);
const indexButton=document.createElement('button');indexButton.className='btn';indexButton.id='translationIndexButton';indexButton.textContent=TUI.index;indexButton.onclick=()=>translationIndex.showModal();modeBar.append(indexButton);
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 if(b.dataset.translationClose)translationIndex.close();
 if(b.dataset.transIndex){translationIndex.close();openOriginal(b.dataset.transIndex,false,indexButton);}
 if(b.dataset.transLink){openOriginal(b.dataset.transLink,false,b);}
 if(b.dataset.transOnpage){const id=b.dataset.transOnpage;originalState.id=id;originalState.page=originalShots[id].page;originalState.zoom=1;renderOriginalViewer(true);}
});
OriginalUI.righttab=TUI.paperTab;OriginalUI.shortcut=TUI.shortcut;U.paper=TUI.paperTab;
document.querySelector('[data-tab="paper"]').textContent=TUI.paperTab;
$('about').insertAdjacentHTML('beforeend',`<p><strong>${esc(TUI.heading)}:</strong> ${esc(TUI.about)}</p>`);
renderSide();renderArgumentContext();if(readerView==='argument')renderArgumentView();
