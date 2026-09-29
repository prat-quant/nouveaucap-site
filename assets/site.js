// Nouveau Cap website: launch waitlist, unsubscribe page and a cookieless visit counter.
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
    bad_link: 'Ce lien de désinscription est incomplet. Écrivez-nous à contact@pixapop.fr, nous vous retirons de la liste.'
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

  // Unsubscribe needs a click, so that link scanners in mailboxes never unsubscribe anyone by accident.
  var leave = document.querySelector('[data-unsubscribe]');
  if (leave) {
    var status = document.querySelector('.wl-status');
    var token = new URLSearchParams(location.search).get('t') || '';
    if (!/^[0-9a-f-]{36}$/i.test(token)) { leave.disabled = true; say(status, 'bad_link'); }
    leave.addEventListener('click', function () {
      leave.disabled = true;
      post(leave.getAttribute('data-endpoint'), { action: 'leave', token: token }).then(function (res) {
        if (res && res.ok) say(status, 'left', true); else { leave.disabled = false; say(status, 'network'); }
      }, function () { leave.disabled = false; say(status, 'network'); });
    });
  }
})();
