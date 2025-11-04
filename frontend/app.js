document.addEventListener('DOMContentLoaded', () => {
  const $ = id => document.getElementById(id);
  const FORM_KEYS = ['title', 'context', 'ai_role', 'additional_info', 'output_format', 'target_audience'];
  let lastGenerateOk = false;
  let historySelectMode = false;

  const fieldIds = ['title', 'context', 'ai_role', 'additional_info', 'output_format'];
  const inputs = fieldIds.map(id => document.getElementById(id)).filter(Boolean);
  const genBtn = document.getElementById('generate');
  const saveBtn = document.getElementById('save');
  const clearBtn = document.getElementById('clear');

  const debounce = (fn, wait = 150) => {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), wait); };
  };

  function countFilled() {
    return inputs.reduce((n, el) => n + (el && el.value && el.value.trim() ? 1 : 0), 0);
  }

  function updateButtons() {
    const ok = countFilled() >= 3;
    if (genBtn) genBtn.disabled = !ok;
    if (saveBtn) saveBtn.disabled = !ok;
  }

  function loadForm() {
    FORM_KEYS.forEach(k => {
      const el = $(k);
      if (!el) return;
      const stored = localStorage.getItem('promptforge.last.' + k);
      if (stored === null) return;
      if (el.tagName === 'SELECT') {
        const values = Array.from(el.options || []).map(opt => opt.value);
        if (values.includes(stored)) {
          el.value = stored;
        } else {
          el.value = '';
          localStorage.removeItem('promptforge.last.' + k);
        }
      } else {
        el.value = stored;
      }
    });
  }

  function saveFormToLocal() {
    FORM_KEYS.forEach(k => {
      const el = $(k);
      if (!el) return;
      const val = el.value;
      if (val && val.trim()) {
        localStorage.setItem('promptforge.last.' + k, val);
      } else {
        localStorage.removeItem('promptforge.last.' + k);
      }
    });
  }

  async function generate() {
    saveFormToLocal();
    const payload = {};
    FORM_KEYS.forEach(k => payload[k] = $(k).value);
    const resp = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.ok) {
      $('crafted').textContent = data.data.ollama_response || '';
      localStorage.setItem('promptforge.last.response', JSON.stringify(data));
      lastGenerateOk = true;
    } else {
      $('crafted').textContent = 'Error: ' + (data.error || JSON.stringify(data));
      lastGenerateOk = false;
    }
    updateActionButtons();
    refreshHistoryUI();
  }

  function copyText() {
    const crafted = $('crafted');
    const t = crafted ? crafted.textContent || '' : '';
    if (!lastGenerateOk || !t.trim()) return;
    navigator.clipboard.writeText(t);
  }

  function sanitizeFilename(title) {
    if (!title) return '';
    let s = title.trim().slice(0, 50);
    s = s.replace(/\s+/g, '_');
    s = s.replace(/[^A-Za-z0-9\-_]/g, '');
    s = s.replace(/_+/g, '_');
    return s;
  }

  function exportTxt() {
    const crafted = $('crafted');
    const t = crafted ? crafted.textContent || '' : '';
    if (!lastGenerateOk || !t.trim()) return;
    const blob = new Blob([t], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const titleEl = $('title');
    const title = titleEl ? titleEl.value : '';
    const safe = sanitizeFilename(title);
    a.href = url;
    a.download = safe ? `${safe}.txt` : 'crafted_prompt.txt';
    a.click();
    URL.revokeObjectURL(url);
  }

  function saveToHistory() {
    const entry = {
      id: Date.now(),
      timestamp: (new Date()).toISOString(),
      title: $('title').value,
      prompt: $('crafted').textContent
    };
    FORM_KEYS.forEach(k => entry[k] = $(k).value);
    const hist = JSON.parse(localStorage.getItem('promptforge.history') || '[]');
    hist.unshift(entry);
    localStorage.setItem('promptforge.history', JSON.stringify(hist.slice(0, 200)));
    refreshHistoryUI();
  }

  function clearForm() {
    FORM_KEYS.forEach(k => {
      const el = $(k);
      if (!el) return;
      if (el.tagName === 'SELECT') {
        el.value = '';
      } else {
        el.value = '';
      }
      localStorage.removeItem('promptforge.last.' + k);
    });
    const crafted = $('crafted');
    if (crafted) crafted.textContent = '';
    lastGenerateOk = false;
    updateActionButtons();
  }

  function refreshHistoryUI() {
    const hist = JSON.parse(localStorage.getItem('promptforge.history') || '[]');
    const ul = $('history');
    ul.innerHTML = '';
    for (const e of hist) {
      const li = document.createElement('li');
      if (historySelectMode) {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.dataset.id = e.id;
        checkbox.addEventListener('change', updateDeleteButtonState);
        li.appendChild(checkbox);
      }
      const text = document.createElement('span');
      text.textContent = `${new Date(e.timestamp).toLocaleString()} — ${e.title || '(no title)'}`;      li.appendChild(text);

      li.addEventListener('click', (event) => {
        if (historySelectMode) {
          const checkbox = li.querySelector('input[type="checkbox"]');
          if (event.target !== checkbox) {
            checkbox.checked = !checkbox.checked;
            updateDeleteButtonState();
          }
        } else {
          $('crafted').textContent = e.prompt;
          FORM_KEYS.forEach(k => {
            const el = $(k);
            if (el) el.value = e[k] || '';
          });
          lastGenerateOk = true;
          updateActionButtons();
          updateButtons();
        }
      });
      ul.appendChild(li);
    }
  }

  function updateActionButtons() {
    const copyBtn = $('copy');
    const exportBtn = $('export');
    const craftedEl = $('crafted');
    const t = craftedEl ? craftedEl.textContent || '' : '';
    const enabled = !!(lastGenerateOk && t.trim());
    if (copyBtn) copyBtn.disabled = !enabled;
    if (exportBtn) exportBtn.disabled = !enabled;
  }

  function toggleHistorySelectMode() {
    historySelectMode = !historySelectMode;
    $('history-section').classList.toggle('select-mode-active', historySelectMode);
    if (!historySelectMode) {
      $('select-all-history').checked = false;
    }
    updateDeleteButtonState();
    refreshHistoryUI();
  }

  function updateDeleteButtonState() {
    const checkboxes = document.querySelectorAll('#history input[type="checkbox"]');
    const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
    $('delete-history').disabled = !anyChecked;
  }

  function deleteSelectedHistory() {
    const checkboxes = document.querySelectorAll('#history input[type="checkbox"]:checked');
    const idsToDelete = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id, 10));
    let hist = JSON.parse(localStorage.getItem('promptforge.history') || '[]');
    hist = hist.filter(e => !idsToDelete.includes(e.id));
    localStorage.setItem('promptforge.history', JSON.stringify(hist));
    toggleHistorySelectMode();
  }

  const debouncedUpdate = debounce(updateButtons, 150);

  inputs.forEach(el => {
    el.addEventListener('input', debouncedUpdate);
    el.addEventListener('change', debouncedUpdate);
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      setTimeout(updateButtons, 0);
    });
  }

  loadForm();
  $('generate').addEventListener('click', generate);
  $('copy').addEventListener('click', copyText);
  $('export').addEventListener('click', exportTxt);
  $('save').addEventListener('click', saveToHistory);
  $('clear').addEventListener('click', () => {
    clearForm();
    refreshHistoryUI();
    updateButtons();
  });
  $('select-history').addEventListener('click', toggleHistorySelectMode);
  $('cancel-select-history').addEventListener('click', toggleHistorySelectMode);
  $('delete-history').addEventListener('click', deleteSelectedHistory);
  $('clear-crafted').addEventListener('click', () => {
    const crafted = $('crafted');
    if (crafted) crafted.textContent = '';
    lastGenerateOk = false;
    updateActionButtons();
  });
  $('select-all-history').addEventListener('change', (e) => {
    const checkboxes = document.querySelectorAll('#history input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = e.target.checked);
    updateDeleteButtonState();
  });

  refreshHistoryUI();
  updateActionButtons();
  updateDeleteButtonState();
  updateButtons();
});