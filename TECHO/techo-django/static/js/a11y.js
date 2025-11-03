(function(){
  const html = document.documentElement;
  const fontVal = document.getElementById('font-val');
  const btnDec = document.getElementById('font-dec');
  const btnInc = document.getElementById('font-inc');
  const btnTheme = document.getElementById('theme-toggle');
  const btnHC = document.getElementById('hc-toggle');

  let size = parseInt(localStorage.getItem('fontSize') || '100', 10);
  let theme = localStorage.getItem('theme') || 'light';
  let hc = localStorage.getItem('hc') === '1';

  function apply(){
    html.style.fontSize = size + '%';
    fontVal.textContent = size + '%';
    html.setAttribute('data-theme', theme);
    html.classList.toggle('hc', hc);
  }
  btnDec.onclick = ()=>{ size = Math.max(85, size-10); localStorage.setItem('fontSize', size); apply(); };
  btnInc.onclick = ()=>{ size = Math.min(140, size+10); localStorage.setItem('fontSize', size); apply(); };
  btnTheme.onclick = ()=>{ theme = theme === 'light' ? 'dark' : 'light'; localStorage.setItem('theme', theme); apply(); };
  btnHC.onclick = ()=>{ hc = !hc; localStorage.setItem('hc', hc ? '1':'0'); apply(); };

  apply();
})();
