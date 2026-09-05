// Coverage is visible even when a PDF or translation cannot be obtained.
if(D.source_layer && D.source_layer.status !== 'provided'){
 const coverageNotice=document.createElement('div');
 coverageNotice.id='sourceLayerNotice';
 coverageNotice.setAttribute('role','note');
 coverageNotice.style.cssText='padding:10px 18px;background:#fff8ec;border-bottom:1px solid #e4d4b7;font-size:12px;line-height:1.8;overflow-wrap:anywhere';
 const coverageLabel=D.language==='en'?'Source / translation coverage: ':'\u539f\u6587\u4e0e\u8bd1\u6587\u8986\u76d6\u8bf4\u660e\uff1a';
 coverageNotice.textContent=coverageLabel+(D.source_layer.reason||D.source_layer.status);
 modeBar.after(coverageNotice);
}
