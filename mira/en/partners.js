const bar=document.getElementById('topbar');const update=()=>bar.classList.toggle('solid',window.scrollY>60);window.addEventListener('scroll',update,{passive:true});update();
