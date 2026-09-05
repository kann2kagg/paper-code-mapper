// Preserve a reading location while the outer language selector rebuilds the localized view.
window.ReaderLanguageBridge={
 capture(){
  const shot=typeof originalState==='undefined'?null:{...originalState,open:originalDialog.open,translationVisible:typeof zhVisible==='undefined'?true:zhVisible,scroll:$('originalViewerStage')?.scrollTop||0,translationScroll:$('originalTranslationPane')?.scrollTop||0};
  return {lesson:D.lessons[current].id,stage,tab,all,demoStep,view:readerView,argument:AR?.nodes?.[argumentIndex]?.id,search:$('search').value,workScroll:$('work').scrollTop,windowScroll:window.scrollY,sidebar:$('sidebar').classList.contains('open'),shot,indexOpen:typeof translationIndex==='undefined'?false:translationIndex.open,
   galleries:[...document.querySelectorAll('.original-source')].map(g=>({ids:g.dataset.shotIds,index:Number(g.dataset.shotIndex)||0}))};
 },
 restore(s){
  if(!s)return;
  if(s.anchor){
   if(s.anchor.startsWith('#logic=')){const i=AR?.nodes?.findIndex(n=>n.id===s.anchor.slice(7));if(i>=0)showArgumentView(i,false);}
   else{const i=D.lessons.findIndex(l=>l.id===s.anchor.slice(1));if(i>=0){select(i,false);showCodeView(false);}}
   return;
  }
  const li=D.lessons.findIndex(l=>l.id===s.lesson);if(li>=0)select(li,false);
  stage=Math.max(0,Math.min(Number(s.stage)||0,D.lessons[current].blocks.length-1));
  tab=['vars','example','paper'].includes(s.tab)?s.tab:'vars';all=!!s.all;demoStep=Number(s.demoStep)||0;
  $('search').value=s.search||'';renderTree();renderCode();renderSide();renderArgumentContext();
  const ai=AR?.nodes?.findIndex(n=>n.id===s.argument);
  if(s.view==='argument'&&ai>=0)showArgumentView(ai,false);else showCodeView(false);
  for(const state of s.galleries||[]){
   for(const g of document.querySelectorAll('.original-source'))if(g.dataset.shotIds===state.ids){g.outerHTML=sourceGallery(state.ids.split(','),state.index);}
  }
  if(s.shot&&s.shot.open&&typeof openOriginal==='function'){
   const v=s.shot;
   openOriginal(v.id,v.mode==='full',null,v.page);
   originalState.zoom=v.zoom;originalState.overlay=v.overlay;translationViewerKey=null;
   renderOriginalViewer();
   if(typeof zhVisible!=='undefined'&&zhVisible!==v.translationVisible)zhToggle.click();
   $('originalViewerStage').scrollTop=v.scroll||0;
   $('originalTranslationPane').scrollTop=v.translationScroll||0;
  }
  if(s.indexOpen&&typeof translationIndex!=='undefined'&&!translationIndex.open)translationIndex.showModal();
  $('sidebar').classList.toggle('open',!!s.sidebar);
  requestAnimationFrame(()=>{$('work').scrollTop=s.workScroll||0;window.scrollTo(0,s.windowScroll||0);});
 }
};
