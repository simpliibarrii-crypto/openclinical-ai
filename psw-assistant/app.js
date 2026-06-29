// openclinical-ai — Home Care Visit Assistant
// Multi-tenant. Voice-first. Browser-only. No build step.
//
// Threat model:
// - All free-text inputs are sanitized for prompt-injection before being sent to AI
// - All API calls include the tenant ID + per-tenant API key
// - Family portal shows only family-visible notes (no PHI, no clinical detail)
// - Visit audit log captures GPS coordinates + timestamps (PHI, encrypted with tenant key)

const state = {
  runtimeUrl: 'http://localhost:8088',
  tenantId: '',
  tenantName: '',
  encryptionModel: '',
  pswId: '',
  authToken: '',
  consentToken: '',
  recognition: null,
  recognizing: false,
  currentVisit: null,
  visitClockIn: null,
};

// -- DOM refs ---------------------------------------------------------------

const els = {
  serverStatus: document.getElementById('server-status'),
  serverStatusText: document.getElementById('server-status-text'),
  tenantBadge: document.getElementById('tenant-badge'),

  // Setup
  tenantSelect: document.getElementById('tenant-select'),
  encryptionIcon: document.getElementById('encryption-icon'),
  encryptionText: document.getElementById('encryption-text'),
  pswId: document.getElementById('psw-id'),
  authMethod: document.getElementById('auth-method'),
  runtimeUrl: document.getElementById('runtime-url'),
  signinBtn: document.getElementById('signin-btn'),
  familyPortalBtn: document.getElementById('family-portal-btn'),
  setupMessage: document.getElementById('setup-message'),

  // Sections
  setupCard: document.getElementById('setup-card'),
  todayCard: document.getElementById('today-card'),
  visitCard: document.getElementById('visit-card'),
  resultCard: document.getElementById('result-card'),
  auditCard: document.getElementById('audit-card'),
  familyCard: document.getElementById('family-card'),

  // Today
  pswLabel: document.getElementById('psw-label'),
  visitList: document.getElementById('visit-list'),
  refreshVisitsBtn: document.getElementById('refresh-visits-btn'),
  signoutBtn: document.getElementById('signout-btn'),

  // Visit
  visitClientLabel: document.getElementById('visit-client-label'),
  visitClockTime: document.getElementById('visit-clock-time'),
  visitStatusBadge: document.getElementById('visit-status-badge'),
  visitAddress: document.getElementById('visit-address'),
  visitGps: document.getElementById('visit-gps'),

  bp: document.getElementById('bp'),
  hr: document.getElementById('hr'),
  temp: document.getElementById('temp'),
  spo2: document.getElementById('spo2'),
  pain: document.getElementById('pain'),
  meal: document.getElementById('meal'),
  ambulation: document.getElementById('ambulation'),
  mood: document.getElementById('mood'),
  notes: document.getElementById('notes'),
  familyVisible: document.getElementById('family-visible'),

  voiceBtn: document.getElementById('voice-btn'),
  voiceBtnText: document.getElementById('voice-btn-text'),
  voiceStatus: document.getElementById('voice-status'),

  generateSummaryBtn: document.getElementById('generate-summary-btn'),
  clockOutBtn: document.getElementById('clock-out-btn'),
  cancelVisitBtn: document.getElementById('cancel-visit-btn'),
  visitMessage: document.getElementById('visit-message'),

  // Result
  resultClientLabel: document.getElementById('result-client-label'),
  resultContent: document.getElementById('result-content'),
  nextVisitBtn: document.getElementById('next-visit-btn'),
  backToTodayBtn: document.getElementById('back-to-today-btn'),

  // Audit
  auditContent: document.getElementById('audit-content'),
  refreshAuditBtn: document.getElementById('refresh-audit-btn'),

  // Family portal
  familyClientLabel: document.getElementById('family-client-label'),
  familyContent: document.getElementById('family-content'),
  familyBackBtn: document.getElementById('family-back-btn'),
};

// -- utilities ---------------------------------------------------------------

function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

function showMessage(el, text, kind) {
  el.textContent = text;
  el.className = `message ${kind || 'info'}`;
  show(el);
  if (kind === 'success') setTimeout(() => hide(el), 4000);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}

// -- prompt-injection sanitization (defense-in-depth) -----------------------

const INJECTION_PATTERNS = [
  /ignore (prior|previous|all) instructions?/i,
  /disregard (your|all) (rules|instructions)/i,
  /you are (now|actually) /i,
  /new instructions?:/i,
  /system:?\s/i,
  /assistant:?\s/i,
  /forget (everything|all)/i,
  /reveal (your|the) (prompt|instructions|system)/i,
  /output (the )?(patient|client)(['s]? )(ssn|sin|health card|address)/i,
  /\bSSN\b|\bSIN\b|\bPHN\b/,
  /password|api[_-]?key|secret/i,
];

function sanitize(text) {
  if (!text) return '';
  let s = String(text);
  let flagged = false;
  for (const pattern of INJECTION_PATTERNS) {
    if (pattern.test(s)) {
      flagged = true;
      s = s.replace(pattern, '[redacted]');
    }
  }
  return { text: s, flagged };
}

// -- API helpers -------------------------------------------------------------

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-Tenant-ID': state.tenantId,
    'X-Tenant-API-Key': state.authToken,
    'X-PSW-ID': state.pswId,
  };
}

async function apiGet(path) {
  const res = await fetch(`${state.runtimeUrl}${path}`, {
    method: 'GET',
    headers: apiHeaders(),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${state.runtimeUrl}${path}`, {
    method: 'POST',
    headers: apiHeaders(),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// -- runtime health ----------------------------------------------------------

async function checkServer() {
  try {
    const res = await fetch(`${state.runtimeUrl}/health`);
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

// -- tenant list (multi-tenant registry) -------------------------------------

async function loadTenants() {
  try {
    const res = await fetch(`${state.runtimeUrl}/v1/tenants`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    els.tenantSelect.innerHTML = '<option value="">— select your agency —</option>' +
      (data.tenants || []).map((t) =>
        `<option value="${escapeHtml(t.id)}" data-name="${escapeHtml(t.name)}" data-encryption="${escapeHtml(t.encryption_model || '')}">${escapeHtml(t.name)}</option>`
      ).join('');
  } catch (e) {
    els.tenantSelect.innerHTML = `<option value="">— runtime unreachable —</option>`;
  }
}

// -- sign in -----------------------------------------------------------------

async function signIn() {
  const tenantOpt = els.tenantSelect.options[els.tenantSelect.selectedIndex];
  if (!tenantOpt || !tenantOpt.value) {
    showMessage(els.setupMessage, 'Pick your agency / tenant first.', 'error');
    return;
  }

  state.tenantId = tenantOpt.value;
  state.tenantName = tenantOpt.dataset.name;
  state.encryptionModel = tenantOpt.dataset.encryption;
  state.pswId = els.pswId.value.trim();
  state.runtimeUrl = els.runtimeUrl.value.trim().replace(/\/$/, '') || 'http://localhost:8088';

  if (!state.pswId) {
    showMessage(els.setupMessage, 'PSW ID is required.', 'error');
    return;
  }

  const ok = await checkServer();
  if (!ok) {
    showMessage(els.setupMessage, `Runtime at ${state.runtimeUrl} is unreachable.`, 'error');
    return;
  }

  // Auth flow varies by selected method
  const authMethod = els.authMethod.value;
  let authResponse;
  try {
    authResponse = await apiPost('/v1/auth/signin', {
      tenant_id: state.tenantId,
      psw_id: state.pswId,
      method: authMethod,
    });
  } catch (e) {
    showMessage(els.setupMessage, `Sign-in failed: ${e.message}`, 'error');
    return;
  }

  state.authToken = authResponse.token;
  state.consentToken = authResponse.consent_token || '';

  // Show tenant badge
  els.tenantBadge.textContent = `${state.tenantName} · BYOK`;
  show(els.tenantBadge);

  // Persist
  try {
    localStorage.setItem('openclinical.session', JSON.stringify({
      runtimeUrl: state.runtimeUrl,
      tenantId: state.tenantId,
      tenantName: state.tenantName,
      encryptionModel: state.encryptionModel,
      pswId: state.pswId,
      authToken: state.authToken,
      consentToken: state.consentToken,
    }));
  } catch (e) {}

  hide(els.setupCard);
  show(els.todayCard);
  show(els.auditCard);
  els.pswLabel.textContent = state.pswId;
  await loadVisits();
  await loadAudit();
}

function restoreSession() {
  try {
    const raw = localStorage.getItem('openclinical.session');
    if (!raw) return false;
    const sess = JSON.parse(raw);
    if (!sess.tenantId || !sess.pswId || !sess.authToken) return false;
    Object.assign(state, sess);
    els.runtimeUrl.value = sess.runtimeUrl;
    els.pswId.value = sess.pswId;
    els.tenantBadge.textContent = `${sess.tenantName} · BYOK`;
    show(els.tenantBadge);
    return true;
  } catch (e) {
    return false;
  }
}

function signOut() {
  try { localStorage.removeItem('openclinical.session'); } catch (e) {}
  location.reload();
}

// -- visits ------------------------------------------------------------------

async function loadVisits() {
  els.visitList.innerHTML = '<div class="summary-box">Loading visits…</div>';
  try {
    const data = await apiGet(`/v1/visits/today?psw_id=${encodeURIComponent(state.pswId)}`);
    renderVisitList(data.visits || []);
  } catch (e) {
    els.visitList.innerHTML = `<div class="summary-box">Could not load visits: ${escapeHtml(e.message)}</div>`;
  }
}

function renderVisitList(visits) {
  if (!visits.length) {
    els.visitList.innerHTML = '<div class="summary-box">No visits scheduled for today.</div>';
    return;
  }
  els.visitList.innerHTML = visits.map((v) => `
    <div class="visit-card" data-visit-id="${escapeHtml(v.id)}">
      <div>
        <span class="visit-time-main">${escapeHtml(v.scheduled_start)} – ${escapeHtml(v.scheduled_end)}</span>
        <span class="visit-status ${escapeHtml(v.status)}">${escapeHtml(v.status)}</span>
      </div>
      <div class="visit-client">${escapeHtml(v.client_name)}</div>
      <div class="visit-meta">${escapeHtml(v.address || '')} · ${escapeHtml(v.service_type || '')}</div>
    </div>
  `).join('');

  for (const card of els.visitList.querySelectorAll('.visit-card')) {
    card.addEventListener('click', () => openVisit(card.dataset.visitId));
  }
}

async function openVisit(visitId) {
  try {
    const visit = await apiGet(`/v1/visits/${encodeURIComponent(visitId)}`);
    state.currentVisit = visit;
    state.visitClockIn = new Date().toISOString();

    els.visitClientLabel.textContent = visit.client_name;
    els.visitAddress.textContent = visit.address || '';

    // GPS check-in
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        const lat = pos.coords.latitude.toFixed(6);
        const lng = pos.coords.longitude.toFixed(6);
        els.visitGps.textContent = `📍 ${lat}, ${lng}`;
        // Log GPS clock-in event
        apiPost('/v1/visits/clock-in', {
          visit_id: visitId,
          psw_id: state.pswId,
          gps_lat: parseFloat(lat),
          gps_lng: parseFloat(lng),
          timestamp: state.visitClockIn,
        }).catch(() => {});
      }, (err) => {
        els.visitGps.textContent = `📍 GPS unavailable (${err.message})`;
      });
    } else {
      els.visitGps.textContent = '📍 GPS not supported';
    }

    els.visitStatusBadge.textContent = 'in-progress';
    els.visitStatusBadge.className = 'visit-status in-progress';

    // Start visit clock display
    updateVisitClock();
    setInterval(updateVisitClock, 1000);

    hide(els.todayCard);
    show(els.visitCard);
    show(els.auditCard);
  } catch (e) {
    showMessage(els.setupMessage, `Could not open visit: ${e.message}`, 'error');
  }
}

function updateVisitClock() {
  if (!state.visitClockIn) return;
  const start = new Date(state.visitClockIn).getTime();
  const now = Date.now();
  const elapsed = Math.floor((now - start) / 1000);
  const h = Math.floor(elapsed / 3600);
  const m = Math.floor((elapsed % 3600) / 60);
  const s = elapsed % 60;
  els.visitClockTime.textContent =
    `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// -- voice input -------------------------------------------------------------

function initVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    els.voiceBtn.disabled = true;
    els.voiceStatus.textContent = 'voice not supported — use Chrome/Edge';
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
  try { state.recognition.start(); } catch (e) {
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

// -- inference + visit completion -------------------------------------------

async function generateSummary() {
  if (!state.currentVisit) return;

  const notesSanitized = sanitize(els.notes.value);
  if (notesSanitized.flagged) {
    showMessage(els.visitMessage, 'Prompt-injection patterns detected in notes — content sanitized before AI processing.', 'info');
  }

  els.generateSummaryBtn.disabled = true;
  els.generateSummaryBtn.textContent = 'Generating…';

  try {
    const res = await apiPost('/v1/inference', {
      tenant_id: state.tenantId,
      model_id: 'psw-shift-handoff',
      patient_id: state.currentVisit.client_id,
      consent_token: state.consentToken,
      inputs: {
        resident_id: state.currentVisit.client_id,
        psw_id: state.pswId,
        visit_id: state.currentVisit.id,
        timestamp: new Date().toISOString(),
        notes: notesSanitized.text,
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
      },
    });

    renderResult(res);
    await loadAudit();
  } catch (e) {
    showMessage(els.visitMessage, `Error: ${e.message}`, 'error');
  } finally {
    els.generateSummaryBtn.disabled = false;
    els.generateSummaryBtn.textContent = 'Generate visit summary';
  }
}

async function clockOut() {
  if (!state.currentVisit) return;

  els.clockOutBtn.disabled = true;
  els.clockOutBtn.textContent = 'Clocking out…';

  try {
    // Generate summary first if not yet
    await generateSummary();

    // Then clock out
    const res = await apiPost('/v1/visits/clock-out', {
      visit_id: state.currentVisit.id,
      psw_id: state.pswId,
      timestamp: new Date().toISOString(),
      family_visible_note: sanitize(els.familyVisible.value).text,
    });

    showMessage(els.visitMessage, `Visit complete. Audit ID: ${res.audit_event_id}`, 'success');
    setTimeout(() => backToToday(), 1500);
  } catch (e) {
    showMessage(els.visitMessage, `Clock-out failed: ${e.message}`, 'error');
  } finally {
    els.clockOutBtn.disabled = false;
    els.clockOutBtn.textContent = 'Clock out + finalize';
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
        <code>tenant: ${escapeHtml(state.tenantId)}</code><br>
        <code>inference_id: ${escapeHtml(data.inference_id)}</code><br>
        <code>audit_event_id: ${escapeHtml(data.audit_event_id)}</code><br>
        <code>latency: ${data.latency_ms}ms</code>
      </div>
    </div>
  `;

  els.resultClientLabel.textContent = state.currentVisit.client_name;
  hide(els.visitCard);
  show(els.resultCard);
}

function backToToday() {
  state.currentVisit = null;
  state.visitClockIn = null;
  hide(els.visitCard);
  hide(els.resultCard);
  show(els.todayCard);
  resetVisitForm();
  loadVisits();
}

function resetVisitForm() {
  for (const id of ['bp', 'hr', 'temp', 'spo2', 'pain', 'meal', 'ambulation', 'mood', 'notes', 'familyVisible']) {
    const el = document.getElementById(id);
    if (el) el.value = '';
  }
  hide(els.visitMessage);
  if (els.visitGps) els.visitGps.textContent = '';
}

// -- audit -------------------------------------------------------------------

async function loadAudit() {
  try {
    const res = await apiGet(`/audit/events?tenant_id=${encodeURIComponent(state.tenantId)}&limit=10`);
    const events = res.events || [];

    if (!events.length) {
      els.auditContent.innerHTML = '<div class="summary-box">No audit events yet for this tenant.</div>';
      return;
    }

    els.auditContent.innerHTML = events.map((e) => `
      <div class="audit-event">
        <span class="event-type ${escapeHtml(e.event_type)}">${escapeHtml(e.event_type)}</span>
        <code>${escapeHtml(e.timestamp)}</code> · ${escapeHtml(e.model_id || e.event_type)}
        ${e.reason ? `<br><small>${escapeHtml(e.reason)}</small>` : ''}
      </div>
    `).join('');
  } catch (e) {
    els.auditContent.innerHTML = `<div class="summary-box">Audit unavailable: ${escapeHtml(e.message)}</div>`;
  }
}

// -- family portal -----------------------------------------------------------

async function openFamilyPortal() {
  hide(els.setupCard);
  hide(els.todayCard);
  hide(els.visitCard);
  hide(els.resultCard);
  hide(els.auditCard);
  show(els.familyCard);

  // Family portal: read-only view of family-visible notes
  // No PHI, no clinical detail, no AI outputs
  els.familyContent.innerHTML = '<div class="summary-box">Loading family-visible visits…</div>';

  try {
    const res = await apiGet(`/v1/family/timeline?token=${encodeURIComponent(state.authToken)}`);
    const visits = res.visits || [];

    if (!visits.length) {
      els.familyContent.innerHTML = '<div class="summary-box">No family-visible visits yet.</div>';
      return;
    }

    els.familyContent.innerHTML = visits.map((v) => `
      <div class="visit-card">
        <div>
          <span class="visit-time-main">${escapeHtml(v.timestamp)}</span>
          <span class="visit-status completed">completed</span>
        </div>
        <div class="visit-client">PSW: ${escapeHtml(v.psw_name || 'caregiver')}</div>
        <div class="visit-meta">
          ${v.family_visible_note ? `<div class="summary-box" style="margin-top:0.5rem;">${escapeHtml(v.family_visible_note)}</div>` : '<em>No family-visible note for this visit.</em>'}
        </div>
      </div>
    `).join('');

    els.familyClientLabel.textContent = res.client_name || 'your loved one';
  } catch (e) {
    els.familyContent.innerHTML = `<div class="summary-box">Family portal unavailable: ${escapeHtml(e.message)}</div>`;
  }
}

function closeFamilyPortal() {
  hide(els.familyCard);
  show(els.setupCard);
}

// -- wiring ------------------------------------------------------------------

els.tenantSelect.addEventListener('change', () => {
  const opt = els.tenantSelect.options[els.tenantSelect.selectedIndex];
  if (!opt || !opt.value) {
    els.encryptionText.textContent = 'select a tenant';
    return;
  }
  const enc = opt.dataset.encryption;
  if (enc === 'agency-byok') {
    els.encryptionIcon.textContent = '🔒';
    els.encryptionText.textContent = 'agency BYOK — agency-held encryption keys';
  } else if (enc === 'platform-managed') {
    els.encryptionIcon.textContent = '🔐';
    els.encryptionText.textContent = 'platform-managed encryption';
  } else {
    els.encryptionIcon.textContent = '🔓';
    els.encryptionText.textContent = 'shared key — not recommended for healthcare';
  }
});

els.signinBtn.addEventListener('click', signIn);
els.signoutBtn.addEventListener('click', signOut);
els.familyPortalBtn.addEventListener('click', openFamilyPortal);
els.familyBackBtn.addEventListener('click', closeFamilyPortal);
els.refreshVisitsBtn.addEventListener('click', loadVisits);
els.generateSummaryBtn.addEventListener('click', generateSummary);
els.clockOutBtn.addEventListener('click', clockOut);
els.cancelVisitBtn.addEventListener('click', backToToday);
els.nextVisitBtn.addEventListener('click', backToToday);
els.backToTodayBtn.addEventListener('click', backToToday);
els.refreshAuditBtn.addEventListener('click', loadAudit);
els.voiceBtn.addEventListener('click', () => {
  if (state.recognizing) stopVoice(); else startVoice();
});

setInterval(checkServer, 5000);

initVoice();
checkServer();
loadTenants();

if (restoreSession()) {
  hide(els.setupCard);
  show(els.todayCard);
  show(els.auditCard);
  els.pswLabel.textContent = state.pswId;
  checkServer();
  loadVisits();
  loadAudit();
}

window.openclinicalSignOut = signOut;