// Public page metrics only. No form values, cookies or visitor identifiers.
// Skip local previews and explicitly marked owner/QA sessions.
if (['wegc.fund', 'www.wegc.fund'].includes(location.hostname)
    && new URLSearchParams(location.search).get('mira_analytics') !== 'off'
    && !document.querySelector('script[data-cf-beacon]')) {
  const beacon = document.createElement('script');
  beacon.type = 'module';
  beacon.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  // This is the public collection token, not an API credential.
  beacon.dataset.cfBeacon = JSON.stringify({token: '07ed230ac0cd41c0be1109c9f740c442'});
  document.head.append(beacon);
}
