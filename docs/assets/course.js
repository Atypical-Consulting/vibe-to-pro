(function(){
  "use strict";
  var isEN = document.documentElement.lang === "en";
  var L = isEN
    ? { done: "Read ✓", verified: "Verified ✓✓", copy: "Copy", copied: "Copied", ago: "days ago" }
    : { done: "Lu ✓", verified: "Vérifié ✓✓", copy: "Copier", copied: "Copié", ago: "j" };

  var MODULES = ["prologue","controle","memoire","skills","plan","agents","hooks","mcp",
                 "rewind","git","echelle","plugins","infra","epilogue"];
  var STORAGE_KEY = "claude-code-course-progress-v1";

  function loadDone(){
    try{ var raw = localStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : {}; }catch(e){ return {}; }
  }
  function saveDone(done){
    try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(done)); }catch(e){}
  }

  function refreshProgressUI(done){
    var count = 0;
    MODULES.forEach(function(m){ if(done[m]) count++; });
    document.querySelectorAll(".chk[data-chk]").forEach(function(chk){
      var m = chk.getAttribute("data-chk");
      chk.classList.toggle("done", !!done[m]);
      chk.classList.toggle("verified", done[m] === "verified");
    });
    document.querySelectorAll(".mark-done[data-mark]").forEach(function(btn){
      var m = btn.getAttribute("data-mark");
      var isDone = !!done[m], isVerified = done[m] === "verified";
      btn.classList.toggle("is-done", isDone);
      btn.textContent = isVerified ? L.verified : (isDone ? L.done : btn.getAttribute("data-label"));
    });
    var pt = document.getElementById("progress-text");
    var pf = document.getElementById("progress-fill");
    if(pt) pt.textContent = count + " / " + MODULES.length;
    if(pf) pf.style.width = (count / MODULES.length * 100) + "%";
  }

  function initProgress(){
    var done = loadDone();
    refreshProgressUI(done);
    document.querySelectorAll(".mark-done").forEach(function(btn){
      if(!btn.hasAttribute("data-label")) btn.setAttribute("data-label", btn.textContent);
      btn.addEventListener("click", function(){
        var m = btn.getAttribute("data-mark");
        done[m] = !done[m];
        saveDone(done);
        refreshProgressUI(done);
      });
    });
  }

  function initQuizzes(){
    var byModule = {};
    document.querySelectorAll(".quiz").forEach(function(quiz){
      var section = quiz.closest(".module");
      var modId = section ? section.id : null;
      if(modId){
        if(!byModule[modId]) byModule[modId] = { total: 0, correct: {} };
        byModule[modId].total++;
        quiz.dataset.quizIdx = byModule[modId].total - 1;
      }
      var btn = quiz.querySelector(".q-check");
      var ok = quiz.querySelector(".q-feedback.ok");
      var bad = quiz.querySelector(".q-feedback.bad");
      if(!btn || !ok || !bad) return;
      btn.addEventListener("click", function(){
        var picked = quiz.querySelector("input[type=radio]:checked");
        ok.style.display = "none";
        bad.style.display = "none";
        if(!picked) return;
        var correct = picked.value === quiz.getAttribute("data-correct");
        (correct ? ok : bad).style.display = "block";
        if(correct && modId){
          byModule[modId].correct[quiz.dataset.quizIdx] = true;
          if(Object.keys(byModule[modId].correct).length === byModule[modId].total){
            var done = loadDone();
            done[modId] = "verified";
            saveDone(done);
            refreshProgressUI(done);
          }
        }
      });
    });
  }

  function initFreshness(){
    document.querySelectorAll("[data-freshness]").forEach(function(el){
      var days = Math.floor((Date.now() - new Date(el.getAttribute("data-freshness"))) / 86400000);
      if(days < 0 || days > 1000) return;
      var tag = document.createElement("b");
      tag.textContent = " · " + days + " " + L.ago;
      el.appendChild(tag);
      if(days > 21) el.style.borderColor = "var(--warn)";
    });
  }

  function initCopyButtons(){
    document.querySelectorAll("pre[class*='language-']").forEach(function(pre){
      if(pre.parentElement.classList.contains("code-block")) return;
      var wrap = document.createElement("div");
      wrap.className = "code-block";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      btn.textContent = L.copy;
      btn.addEventListener("click", function(){
        var code = pre.querySelector("code");
        var text = code ? code.textContent : pre.textContent;
        navigator.clipboard.writeText(text).then(function(){
          btn.textContent = L.copied;
          btn.classList.add("copied");
          setTimeout(function(){ btn.textContent = L.copy; btn.classList.remove("copied"); }, 1600);
        }).catch(function(){});
      });
      wrap.appendChild(btn);
    });
  }

  document.addEventListener("DOMContentLoaded", function(){
    if(window.Prism) Prism.highlightAll();
    initProgress();
    initQuizzes();
    initFreshness();
    initCopyButtons();
  });
})();
