'use strict';
// Locale text was authored and validated at build time. No browser translation or network calls.
const LB=JSON.parse(document.getElementById('languageBundle').textContent);
const LOC=LB.localization, frame=document.getElementById('readerFrame');
const readingSelect=document.getElementById('readingLanguage'), translationSelect=document.getElementById('translationLanguage');
const clone=x=>JSON.parse(JSON.stringify(x));
let reading=LOC.default_reading, translation=LOC.default_translation||'', readerSnapshot=null;
try{const stored=JSON.parse(localStorage.getItem(LB.storage_key)||'null');if(stored){if(LOC.readings[stored.reading])reading=stored.reading;if(LOC.translations[stored.translation])translation=stored.translation;}}catch{}
function option(value,label){const o=document.createElement('option');o.value=value;o.textContent=label;return o;}
for(const [lang,x]of Object.entries(LOC.readings))readingSelect.append(option(lang,x.label));
for(const [lang,x]of Object.entries(LOC.translations))translationSelect.append(option(lang,x.label));
function safeData(d){return JSON.stringify(d).replace(/&/g,'\\u0026').replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');}
function localizedData(){
 const data=clone(LB.base);
 for(const [path,text]of Object.entries(LOC.readings[reading].patch||{})){
  const keys=path.slice(1).split('/');let obj=data;
  for(const key of keys.slice(0,-1))obj=obj[key];
  obj[keys[keys.length-1]]=text;
 }
 data.language=reading;
 if(translation){data.screenshot_translations=clone(LOC.translations[translation].regions);data.source_layer.translation_language=translation;}
 Object.assign(data,clone(LB.catalogs[reading][translation]));
 return data;
}
function labels(){
 const ui=LB.catalogs[reading][translation].shell_ui;
 readingSelect.value=reading;translationSelect.value=translation;
 document.documentElement.lang=reading;document.documentElement.dir=LOC.readings[reading].direction||'ltr';
 document.getElementById('languageBrand').textContent=ui.brand;
 document.getElementById('readingLabel').textContent=ui.reading;
 document.getElementById('translationLabel').textContent=ui.translationSelect;
 document.getElementById('languageNote').textContent=ui.offline;
 document.querySelector('.languagebar').setAttribute('aria-label',ui.settings);
 frame.title=ui.readerTitle;
 document.getElementById('translationControl').hidden=!translation;
}
function savePreference(){try{localStorage.setItem(LB.storage_key,JSON.stringify({reading,translation}));}catch{}}
function loadReader(preserve=true){
 if(preserve){try{readerSnapshot=frame.contentWindow.ReaderLanguageBridge?.capture()||readerSnapshot;}catch{}}
 labels();savePreference();
 const data=localizedData();document.title=data.title;
 frame.srcdoc=LB.template.replace('__LOCALIZED_DATA__',()=>safeData(data));
}
frame.addEventListener('load',()=>{
 const ui=LB.catalogs[reading][translation].shell_ui;
 try{
  const bridge=frame.contentWindow.ReaderLanguageBridge;
  if(!bridge)throw new Error('Reader state bridge did not initialize');
  if(readerSnapshot)bridge.restore(readerSnapshot);else if(location.hash)bridge.restore({anchor:location.hash});
  document.getElementById('languageStatus').textContent='';
  frame.dataset.ready='true';
 }catch(e){document.getElementById('languageStatus').textContent=ui.failure+' '+e.message;}
});
readingSelect.addEventListener('change',()=>{reading=readingSelect.value;frame.dataset.ready='false';loadReader();});
translationSelect.addEventListener('change',()=>{translation=translationSelect.value;frame.dataset.ready='false';loadReader();});
window.addEventListener('message',e=>{
 if(e.source!==frame.contentWindow||e.data?.type!=='pcmr-anchor')return;
 const hash=e.data.hash;
 if(typeof hash==='string'&&/^#(?:logic=)?[A-Za-z0-9_.-]+$/.test(hash)){
  try{history.replaceState(null,'',hash);}catch{}
 }
});
window.addEventListener('hashchange',()=>{try{frame.contentWindow.ReaderLanguageBridge?.restore({anchor:location.hash});}catch{}});
loadReader(false);
