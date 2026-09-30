// Nouveau Cap website: launch waitlist, free PDF guides, unsubscribe page and a cookieless visit counter.
(function () {
  // Visit counter: sends only the page path and the referring site's name. No cookie, nothing stored on
  // the device, no identifier. Skipped when the browser asks not to be tracked, and on local previews.
  var endpoint = document.body.getAttribute('data-visit');
  var optOut = navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  var local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  if (endpoint && !optOut && !local && navigator.sendBeacon) {
    var ref = '';
    try { if (document.referrer) { var h = new URL(document.referrer).hostname; if (h !== location.hostname) ref = h; } } catch (e) {}
    try { navigator.sendBeacon(endpoint, JSON.stringify({ p: location.pathname, r: ref })); } catch (e) {}
  }

  var MESSAGES = {
    ok: 'C’est noté. Vous recevrez un seul e-mail, le jour du lancement.',
    invalid_email: 'Cette adresse e-mail ne semble pas valide. Vérifiez-la et réessayez.',
    no_consent: 'Cochez la case pour que nous puissions vous écrire.',
    rate_limited: 'Trop d’essais depuis cette connexion. Réessayez dans une heure.',
    network: 'L’envoi n’a pas abouti. Vérifiez votre connexion et réessayez.',
    left: 'C’est fait : votre adresse a été effacée de la liste.',
    left_guide: 'C’est fait : vous ne recevrez plus nos nouvelles. Votre adresse sera effacée dans 30 jours.',
    bad_link: 'Ce lien de désinscription est incomplet. Écrivez-nous à contact@pixapop.fr, nous vous retirons de la liste.',
    guide_sent: 'C’est envoyé. Le guide arrive dans quelques minutes à l’adresse indiquée (pensez à regarder dans les indésirables).',
    guide_ready: 'Votre guide est prêt\u00a0: ',
    guide_link: 'Télécharger le PDF',
    bad_guide: 'Ce guide n’est pas disponible pour le moment. Écrivez-nous à contact@pixapop.fr, nous vous l’envoyons.',
    guide_no_consent: 'Votre accord pour les nouvelles n’a pas été transmis. Rechargez la page et réessayez, ou décochez la case.',
    server: 'Le service est momentanément indisponible. Réessayez dans quelques minutes.'
  };
  function say(el, key, ok) {
    el.textContent = MESSAGES[key] || MESSAGES.network;
    el.className = 'wl-status ' + (ok ? 'ok' : 'err');
  }
  function post(url, payload) {
    return fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json().catch(function () { return { ok: false, error: 'network' }; }); });
  }

  document.querySelectorAll('form[data-waitlist]').forEach(function (form) {
    var status = form.querySelector('.wl-status');
    var button = form.querySelector('button[type=submit]');
    var email = form.elements.email;
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var value = email.value.trim();
      email.removeAttribute('aria-invalid');
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) { email.setAttribute('aria-invalid', 'true'); email.focus(); return say(status, 'invalid_email'); }
      if (!form.elements.consent.checked) return say(status, 'no_consent');
      var platform = form.querySelector('input[name=platform]:checked');
      button.disabled = true;
      status.textContent = 'Envoi…'; status.className = 'wl-status';
      post(form.getAttribute('data-endpoint'), {
        action: 'join', app: form.getAttribute('data-app'), source: form.getAttribute('data-source'),
        email: value, platform: platform ? platform.value : '', website: form.elements.website.value,
        consent: form.querySelector('[data-consent]').textContent
      }).then(function (res) {
        if (res && res.ok) { say(status, 'ok', true); form.reset(); }
        else say(status, res && res.error);
      }, function () { say(status, 'network'); })
        .then(function () { button.disabled = false; });
    });
  });

  // Free PDF guides: the guide is always sent; the news only with the separate, unticked box (CNIL rule).
  // When e-mail sending is unavailable, the server returns a direct link, shown without any innerHTML.
  document.querySelectorAll('form[data-guide-form]').forEach(function (form) {
    var status = form.querySelector('.wl-status');
    var button = form.querySelector('button[type=submit]');
    var email = form.elements.email;
    function ready(url) {
      var a = document.createElement('a');
      a.href = url; a.target = '_blank'; a.rel = 'noopener'; a.textContent = MESSAGES.guide_link;
      status.textContent = MESSAGES.guide_ready;
      status.appendChild(a);
      status.className = 'wl-status ok';
    }
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var value = email.value.trim();
      email.removeAttribute('aria-invalid');
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value)) { email.setAttribute('aria-invalid', 'true'); email.focus(); return say(status, 'invalid_email'); }
      var news = form.elements.news.checked;
      var payload = {
        action: 'request', app: 'nouveau-cap', guide: form.getAttribute('data-guide'), email: value, news: news,
        source: form.getAttribute('data-source'), website: form.elements.website.value
      };
      if (news) payload.consent = form.querySelector('[data-consent]').textContent;
      button.disabled = true;
      status.textContent = 'Envoi…'; status.className = 'wl-status';
      post(form.getAttribute('data-endpoint'), payload).then(function (res) {
        if (res && res.ok && res.sent) { say(status, 'guide_sent', true); form.reset(); }
        else if (res && res.ok && typeof res.url === 'string' && /^https:\/\//.test(res.url)) { ready(res.url); form.reset(); }
        else if (res && res.ok) say(status, 'server');
        else say(status, res && (res.error === 'no_consent' ? 'guide_no_consent' : res.error));
      }, function () { say(status, 'network'); })
        .then(function () { button.disabled = false; });
    });
  });

  // Unsubscribe needs a click, so that link scanners in mailboxes never unsubscribe anyone by accident.
  var leave = document.querySelector('[data-unsubscribe]');
  if (leave) {
    var status = document.querySelector('.wl-status');
    var params = new URLSearchParams(location.search), token = params.get('t') || '';
    // Links in guide e-mails carry k=guide: they stop the news, the guide itself stays yours.
    var endpoint = leave.getAttribute('data-endpoint'), done = 'left';
    if (params.get('k') === 'guide') {
      endpoint = leave.getAttribute('data-endpoint-guide'); done = 'left_guide';
      document.querySelector('[data-unsub-kind]').textContent = 'Guides Nouveau Cap';
      document.querySelector('[data-unsub-lead]').textContent = 'Vous ne recevrez plus nos nouvelles (lancement de l’application, prochains guides). Votre adresse sera effacée dans 30 jours.';
    }
    if (!/^[0-9a-f-]{36}$/i.test(token)) { leave.disabled = true; say(status, 'bad_link'); }
    leave.addEventListener('click', function () {
      leave.disabled = true;
      post(endpoint, { action: 'leave', token: token }).then(function (res) {
        if (res && res.ok) say(status, done, true); else { leave.disabled = false; say(status, 'network'); }
      }, function () { leave.disabled = false; say(status, 'network'); });
    });
  }
})();

// Runway calculator (blog): how many months the household can hold, month by month, with the ARE
// allowance until the end of the rights, then without. Runs on the device only; nothing is sent.
function nouveauCapRunway(v) {
  var n = function (x) { x = Number(x); return isFinite(x) && x > 0 ? x : 0; };
  var savings = Math.max(0, n(v.savings) - n(v.reserve)), expenses = n(v.expenses), are = n(v.are);
  var months = Math.floor(n(v.months)), income = n(v.income);
  var during = income + are - expenses, after = income - expenses;
  if (expenses === 0) return { status: 'empty' };
  if (after >= 0) return { status: 'covered', during: during, after: after };
  var balance = savings;
  for (var m = 1; m <= 600; m++) {
    balance += income + (m <= months ? are : 0) - expenses;
    if (balance < 0) return { status: 'ok', runway: m - 1, during: during, after: after, arePart: Math.min(m - 1, months) };
  }
  return { status: 'long', runway: 600, during: during, after: after };
}
if (typeof module !== 'undefined') module.exports = nouveauCapRunway;

(function () {
  if (typeof document === 'undefined') return;
  var MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
  var euro = function (x) { return Math.round(Math.abs(x)).toLocaleString('fr-FR') + ' €'; };
  document.querySelectorAll('[data-calc]').forEach(function (box) {
    var out = function (k) { return box.querySelector('[data-out="' + k + '"]'); };
    function update() {
      var v = {};
      box.querySelectorAll('input').forEach(function (i) { v[i.name] = i.value; });
      var r = nouveauCapRunway(v);
      if (r.status === 'empty') { out('runway').textContent = 'Renseignez vos dépenses'; out('detail').textContent = ''; return; }
      if (r.status === 'covered') {
        out('runway').textContent = 'Vos revenus couvrent vos dépenses';
        out('detail').textContent = 'Même sans allocation, vos autres revenus couvrent vos dépenses mensuelles : votre épargne n’est pas entamée.';
        return;
      }
      var m = r.runway, d = new Date(); d.setMonth(d.getMonth() + m);
      out('runway').textContent = m >= 600 ? 'Plus de 50 ans' : (m + ' mois');
      var parts = [];
      if (r.during >= 0) parts.push('Pendant vos droits ARE, vos revenus couvrent vos dépenses.');
      else parts.push('Pendant vos droits ARE : il vous manque ' + euro(r.during) + ' par mois.');
      parts.push('Ensuite : il vous manque ' + euro(r.after) + ' par mois.');
      if (m < 600) parts.push('Épargne mobilisable épuisée vers ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear() + ' (hors montant gardé de côté).');
      out('detail').textContent = parts.join(' ');
    }
    box.addEventListener('input', update);
    update();
  });
})();
