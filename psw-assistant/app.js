// openclinical-ai — PSW Shift Handoff Assistant
// Pure browser app. No build step. No external deps.
// Talks to the local runtime over fetch().

const state = {
  runtimeUrl: 'http://localhost:8088',
  pswId: '',
  residentId: '',
  consentToken: '',
  recognition: null,
  recognizing: false,
};

// -- DOM refs ---------------------------------------------------------------

const els = {
  serverStatus: document.getElementById('server-status'),
  serverStatusText: document.getElementById('server-status-text'),

  pswId: document.getElementById('psw-id'),
  residentId: document.getElementById('resident-id'),
  runtimeUrl: document.getElementById('runtime-url'),
  grantConsentBtn: document.getElementById('grant-consent-btn'),
  setupMessage: document.getElementById('setup-message'),

  setupCard: document.getElementById('setup-card'),
  handoffCard: document.getElementById('handoff-card'),
  resultCard: document.getElementById('result-card'),
  auditCard: document.getElementById('audit-card'),

  residentLabel: document.getElementById('resident-label'),

  bp: document.getElementById('bp'),
  hr: document.getElementById('hr'),
  temp: document.getElementById('temp'),
  spo2: document.getElementById('spo2'),
  pain: document.getElementById('pain'),
  meal: document.getElementById('meal'),
  ambulation: document.getElementById('ambulation'),
  mood: document.getElementById('mood'),
  notes: document.getElementById('notes'),

  voiceBtn: document.getElementById('voice-btn'),
  voiceBtnText: document.getElementById('voice-btn-text'),
  voiceStatus: document.getElementById('voice-status'),

  submitBtn: document.getElementById('submit-btn'),
  resetBtn: document.getElementById('reset-btn'),
  handoffMessage: document.getElementById('handoff-message'),

  resultContent: document.getElementById('result-content'),
  newHandoffBtn: document.getElementById('new-handoff-btn'),

  auditContent: document.getElementById('audit-content'),
  refreshAuditBtn: document.getElementById('refresh-audit-btn'),
};

// -- utilities ---------------------------------------------------------------

function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

function showMessage(el, text, kind) {
  el.textContent = text;
  el.className = `message ${kind || 'info'}`;
  show(el);
  if (kind === 'success') {
    setTimeout(() => hide(el), 4000);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}

// -- runtime health ----------------------------------------------------------

async function checkServer() {
  try {
    const res = await fetch(`${state.runtimeUrl}/health`, { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    els.serverStatus.className = 'status-dot status-healthy';
    els.serverStatusText.textContent = `runtime v${data.version} · ${data.models_loaded} model(s)`;
    return true;
  } catch (e) {
    els.serverStatus.className = 'status-dot status-error';
    els.serverStatusText.textContent = 'runtime unreachable';
    return false;
  }
}

// -- consent -----------------------------------------------------------------

async function grantConsent() {
  state.pswId = els.pswId.value.trim();
  state.residentId = els.residentId.value.trim();
  state.runtimeUrl = els.runtimeUrl.value.trim().replace(/\/$/, '') || 'http://localhost:8088';

  if (!state.pswId || !state.residentId) {
    showMessage(els.setupMessage, 'PSW ID and Resident ID are required.', 'error');
    return;
  }

  const ok = await checkServer();
  if (!ok) {
    showMessage(els.setupMessage, `Runtime at ${state.runtimeUrl} is unreachable.`, 'error');
    return;
  }

  // Grant consent via runtime's consent endpoint (POST /consent/grant).
  // For MVP, the runtime exposes consent via a direct tool (tools/grant_consent.py)
  // — but we also support a server-side grant via /v1/consent/grant for browser UX.
  try {
    const res = await fetch(`${state.runtimeUrl}/v1/consent/grant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: state.residentId,
        scope: ['*'],
        granted_by: state.pswId,
      }),
    });
    if (!res.ok) {
      // Fallback: if /v1/consent/grant isn't available, prompt for an existing token.
      const t = prompt(
        'Consent endpoint not available. Paste a consent token (from `python3 tools/grant_consent.py ' +
        state.residentId + ' ' + state.pswId + '`):'
      );
      if (!t) {
        showMessage(els.setupMessage, 'Consent required to continue.', 'error');
        return;
      }
      state.consentToken = t.trim();
    } else {
      const data = await res.json();
      state.consentToken = data.token;
    }
  } catch (e) {
    showMessage(els.setupMessage, `Consent grant failed: ${e.message}`, 'error');
    return;
  }

  // Persist in localStorage so reloading doesn't lose session
  try {
    localStorage.setItem('openclinical.session', JSON.stringify({
      runtimeUrl: state.runtimeUrl,
      pswId: state.pswId,
      residentId: state.residentId,
      consentToken: state.consentToken,
    }));
  } catch (e) { /* localStorage unavailable, continue anyway */ }

  hide(els.setupCard);
  els.residentLabel.textContent = state.residentId;
  show(els.handoffCard);
  show(els.auditCard);
  await loadAudit();
}

// Restore session from localStorage if present
function restoreSession() {
  try {
    const raw = localStorage.getItem('openclinical.session');
    if (!raw) return false;
    const sess = JSON.parse(raw);
    if (!sess.runtimeUrl || !sess.pswId || !sess.residentId || !sess.consentToken) return false;
    Object.assign(state, sess);
    els.runtimeUrl.value = sess.runtimeUrl;
    els.pswId.value = sess.pswId;
    els.residentId.value = sess.residentId;
    return true;
  } catch (e) {
    return false;
  }
}

function clearSession() {
  try { localStorage.removeItem('openclinical.session'); } catch (e) {}
  location.reload();
}

// -- voice input -------------------------------------------------------------

function initVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    els.voiceBtn.disabled = true;
    els.voiceStatus.textContent = 'voice input not supported in this browser — use Chrome/Edge for dictation';
    return;
  }

  state.recognition = new SpeechRecognition();
  state.recognition.continuous = true;
  state.recognition.interimResults = true;
  state.recognition.lang = 'en-US';

  let finalTranscript = '';

  state.recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript + ' ';
      } else {
        interim += transcript;
      }
    }
    els.notes.value = (els.notes.value || '') + (finalTranscript || '') + interim;
    if (finalTranscript) finalTranscript = '';
  };

  state.recognition.onerror = (event) => {
    els.voiceStatus.textContent = `voice error: ${event.error}`;
    stopVoice();
  };

  state.recognition.onend = () => {
    if (state.recognizing) {
      // Auto-restart while user expects continuous
      try { state.recognition.start(); } catch (e) {}
    } else {
      els.voiceBtn.classList.remove('recording');
      els.voiceBtnText.textContent = 'Start dictation';
      els.voiceStatus.textContent = '';
    }
  };
}

function startVoice() {
  if (!state.recognition) return;
  state.recognizing = true;
  els.voiceBtn.classList.add('recording');
  els.voiceBtnText.textContent = 'Stop dictation';
  els.voiceStatus.textContent = 'listening…';
  try {
    state.recognition.start();
  } catch (e) {
    els.voiceStatus.textContent = `voice start failed: ${e.message}`;
    stopVoice();
  }
}

function stopVoice() {
  state.recognizing = false;
  if (state.recognition) {
    try { state.recognition.stop(); } catch (e) {}
  }
  els.voiceBtn.classList.remove('recording');
  els.voiceBtnText.textContent = 'Start dictation';
  els.voiceStatus.textContent = '';
}

// -- inference ---------------------------------------------------------------

function buildInputs() {
  return {
    resident_id: state.residentId,
    psw_id: state.pswId,
    timestamp: new Date().toISOString(),
    notes: els.notes.value || '',
    observations: {
      bp: els.bp.value || null,
      hr: els.hr.value || null,
      temp_c: els.temp.value || null,
      spo2: els.spo2.value ? `${els.spo2.value}%` : null,
      pain: els.pain.value || null,
      meal_pct: els.meal.value || null,
      ambulation: els.ambulation.value || null,
      mood: els.mood.value || null,
    },
  };
}

async function submitHandoff() {
  const inputs = buildInputs();
  if (!inputs.notes && !inputs.observations.bp && !inputs.observations.hr) {
    showMessage(els.handoffMessage, 'Add at least one observation or a note before generating a summary.', 'error');
    return;
  }

  els.submitBtn.disabled = true;
  els.submitBtn.textContent = 'Generating…';

  try {
    const res = await fetch(`${state.runtimeUrl}/v1/inference`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_id: 'psw-shift-handoff',
        patient_id: state.residentId,
        consent_token: state.consentToken,
        inputs,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      showMessage(els.handoffMessage, `Error: ${data.detail || res.statusText}`, 'error');
      return;
    }

    renderResult(data);
    await loadAudit();
  } catch (e) {
    showMessage(els.handoffMessage, `Network error: ${e.message}`, 'error');
  } finally {
    els.submitBtn.disabled = false;
    els.submitBtn.textContent = 'Generate handoff summary';
  }
}

function renderResult(data) {
  const handoff = data.outputs?.shift_handoff || {};
  const concerns = handoff.concerns || [];
  const observations = handoff.structured_observations || {};

  const concernsHtml = concerns.length
    ? concerns.map((c) => `
        <div class="concern ${escapeHtml(c.severity)}">
          <span class="severity">${escapeHtml(c.severity)}</span>
          <strong>${escapeHtml(c.type)}</strong>: ${escapeHtml(c.detail)}
        </div>
      `).join('')
    : '<div class="summary-box">No clinical concerns flagged.</div>';

  const vitals = observations.vitals || {};
  const vitalsHtml = `
    <div class="summary-box">
      <strong>Vitals:</strong>
      ${vitals.bp ? `BP ${escapeHtml(vitals.bp)} · ` : ''}
      ${vitals.hr ? `HR ${escapeHtml(vitals.hr)} · ` : ''}
      ${vitals.temp_c ? `Temp ${escapeHtml(vitals.temp_c)}°C · ` : ''}
      ${vitals.spo2 ? `SpO2 ${escapeHtml(vitals.spo2)} · ` : ''}
      ${vitals.pain ? `Pain ${escapeHtml(vitals.pain)}/10` : ''}
    </div>
  `;

  els.resultContent.innerHTML = `
    <div class="result-section">
      <h3>Summary</h3>
      <div class="summary-box">${escapeHtml(handoff.summary || '(no summary)')}</div>
    </div>
    <div class="result-section">
      <h3>Vitals captured</h3>
      ${vitalsHtml}
    </div>
    <div class="result-section">
      <h3>${concerns.length ? 'Concerns flagged' : 'Concerns'}</h3>
      ${concernsHtml}
    </div>
    <div class="result-section">
      <h3>Audit</h3>
      <div class="summary-box">
        <code>inference_id: ${escapeHtml(data.inference_id)}</code><br>
        <code>audit_event_id: ${escapeHtml(data.audit_event_id)}</code><br>
        <code>latency: ${data.latency_ms}ms</code>
      </div>
    </div>
  `;

  hide(els.handoffCard);
  show(els.resultCard);
}

// -- audit -------------------------------------------------------------------

async function loadAudit() {
  try {
    const res = await fetch(`${state.runtimeUrl}/audit/events?patient_id=${encodeURIComponent(state.residentId)}&limit=10`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const events = data.events || [];

    if (!events.length) {
      els.auditContent.innerHTML = '<div class="summary-box">No audit events yet for this resident on this device.</div>';
      return;
    }

    els.auditContent.innerHTML = events.map((e) => `
      <div class="audit-event">
        <span class="event-type ${escapeHtml(e.event_type)}">${escapeHtml(e.event_type)}</span>
        <code>${escapeHtml(e.timestamp)}</code> · ${escapeHtml(e.model_id || '')} v${escapeHtml(e.model_version || '')}
        ${e.reason ? `<br><small>${escapeHtml(e.reason)}</small>` : ''}
      </div>
    `).join('');
  } catch (e) {
    els.auditContent.innerHTML = `<div class="summary-box">Audit unavailable: ${escapeHtml(e.message)}</div>`;
  }
}

// -- reset -------------------------------------------------------------------

function resetForm() {
  for (const id of ['bp', 'hr', 'temp', 'spo2', 'pain', 'meal', 'ambulation', 'mood', 'notes']) {
    els[id].value = '';
  }
  hide(els.handoffMessage);
  els.notes.focus();
}

function newHandoff() {
  resetForm();
  hide(els.resultCard);
  show(els.handoffCard);
  els.notes.focus();
}

// -- wiring ------------------------------------------------------------------

els.grantConsentBtn.addEventListener('click', grantConsent);
els.submitBtn.addEventListener('click', submitHandoff);
els.resetBtn.addEventListener('click', resetForm);
els.newHandoffBtn.addEventListener('click', newHandoff);
els.refreshAuditBtn.addEventListener('click', loadAudit);
els.voiceBtn.addEventListener('click', () => {
  if (state.recognizing) stopVoice(); else startVoice();
});

// Periodic health check
setInterval(checkServer, 5000);

initVoice();
checkServer();

// If we have a session in localStorage, skip setup
if (restoreSession()) {
  hide(els.setupCard);
  els.residentLabel.textContent = state.residentId;
  show(els.handoffCard);
  show(els.auditCard);
  checkServer();
  loadAudit();
}

// Expose a sign-out for completeness
window.openclinicalSignOut = clearSession;