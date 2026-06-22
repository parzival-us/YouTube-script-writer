const form = document.querySelector('#generator-form');
const topicInput = document.querySelector('#topic');
const topicCount = document.querySelector('#topic-count');
const topicError = document.querySelector('#topic-error');
const generateButton = document.querySelector('#generate-button');
const emptyState = document.querySelector('#empty-state');
const loadingState = document.querySelector('#loading-state');
const scriptResult = document.querySelector('#script-result');
const historyList = document.querySelector('#history-list');
const downloadButton = document.querySelector('#download-button');
const downloadMenu = document.querySelector('#download-menu');
const toast = document.querySelector('#toast');

let currentScript = null;
let toastTimer = null;
let loadingMessageTimer = null;

const loadingMessages = [
  'Finding the strongest angle…',
  'Building a satisfying story arc…',
  'Polishing titles and hooks…',
];

function showToast(message, isError = false) {
  clearTimeout(toastTimer);
  toast.classList.toggle('error', isError);
  toast.querySelector('span').textContent = isError ? '!' : '✓';
  toast.querySelector('p').textContent = message;
  toast.classList.add('visible');
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3200);
}

function setLoading(isLoading) {
  generateButton.disabled = isLoading;
  generateButton.classList.toggle('loading', isLoading);
  emptyState.hidden = true;
  scriptResult.hidden = true;
  loadingState.hidden = !isLoading;

  clearInterval(loadingMessageTimer);
  if (isLoading) {
    let messageIndex = 0;
    document.querySelector('#loading-message').textContent = loadingMessages[0];
    loadingMessageTimer = setInterval(() => {
      messageIndex = (messageIndex + 1) % loadingMessages.length;
      document.querySelector('#loading-message').textContent = loadingMessages[messageIndex];
    }, 1000);
  }
}

function validateTopic() {
  const topic = topicInput.value.trim();
  let message = '';
  if (!topic) message = 'Add a topic to start generating.';
  else if (topic.length < 3) message = 'Please use at least 3 characters.';
  topicInput.classList.toggle('invalid', Boolean(message));
  topicError.textContent = message;
  return !message;
}

function formatMainContent(content) {
  const fragments = content.split('\n\n');
  const container = document.createDocumentFragment();
  const headingPattern = /^(?:\d+\.\s)?(?:The big picture|What most people miss|The practical framework|A real-world example|Common mistakes|The smarter approach|Your next move)$/;
  fragments.forEach((fragment) => {
    const element = document.createElement(headingPattern.test(fragment) ? 'h4' : 'p');
    element.textContent = fragment;
    container.append(element);
  });
  return container;
}

function renderScript(script) {
  currentScript = script;
  loadingState.hidden = true;
  emptyState.hidden = true;
  scriptResult.hidden = false;

  document.querySelector('#result-topic').textContent = script.topic;
  document.querySelector('#result-style').textContent = script.style;
  document.querySelector('#result-length').textContent = script.length;
  document.querySelector('#result-words').textContent = `${script.word_count} words`;
  document.querySelector('#result-runtime').textContent = `~${script.estimated_minutes} min`;
  document.querySelector('#result-hook').textContent = script.hook;
  document.querySelector('#result-introduction').textContent = script.introduction;
  document.querySelector('#result-cta').textContent = script.call_to_action;

  const main = document.querySelector('#result-main');
  main.replaceChildren(formatMainContent(script.main_content));

  const titles = document.querySelector('#result-titles');
  titles.replaceChildren(...script.titles.map((title) => {
    const item = document.createElement('li');
    item.textContent = title;
    return item;
  }));

  const thumbnails = document.querySelector('#result-thumbnails');
  thumbnails.replaceChildren(...script.thumbnail_ideas.map((idea) => {
    const item = document.createElement('span');
    item.textContent = idea;
    return item;
  }));

  document.querySelector('#download-txt').href = `/api/scripts/${script.id}/download.txt`;
  document.querySelector('#download-pdf').href = `/api/scripts/${script.id}/download.pdf`;
  if (window.innerWidth < 741) {
    document.querySelector('#result-panel').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

async function parseError(response) {
  try {
    const data = await response.json();
    if (Array.isArray(data.detail)) return data.detail[0]?.msg || 'Please check your input.';
    return data.detail || 'Something went wrong. Please try again.';
  } catch {
    return 'The server returned an unexpected response.';
  }
}

async function loadHistory() {
  try {
    const response = await fetch('/api/scripts?limit=8');
    if (!response.ok) throw new Error('History could not be loaded');
    const items = await response.json();
    if (!items.length) {
      historyList.innerHTML = '<p class="empty-history">Your saved scripts will appear here.</p>';
      return;
    }
    historyList.replaceChildren(...items.map((item) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'history-item';
      button.dataset.id = item.id;

      const icon = document.createElement('span');
      icon.textContent = '▶';
      const text = document.createElement('div');
      const title = document.createElement('strong');
      title.textContent = item.topic;
      const meta = document.createElement('small');
      meta.textContent = `${item.style} · ${item.length} · ${item.word_count} words`;
      text.append(title, meta);
      button.append(icon, text);
      return button;
    }));
  } catch {
    historyList.innerHTML = '<p class="empty-history">Couldn’t load saved scripts.</p>';
  }
}

async function openSavedScript(scriptId) {
  setLoading(true);
  try {
    const response = await fetch(`/api/scripts/${scriptId}`);
    if (!response.ok) throw new Error(await parseError(response));
    renderScript(await response.json());
  } catch (error) {
    loadingState.hidden = true;
    emptyState.hidden = false;
    showToast(error.message, true);
  } finally {
    generateButton.disabled = false;
    generateButton.classList.remove('loading');
    clearInterval(loadingMessageTimer);
  }
}

topicInput.addEventListener('input', () => {
  topicCount.textContent = `${topicInput.value.length} / 180`;
  if (topicInput.classList.contains('invalid')) validateTopic();
});

document.querySelectorAll('input[name="length"]').forEach((input) => {
  input.addEventListener('change', () => {
    document.querySelectorAll('.length-option').forEach((option) => {
      option.classList.toggle('selected', option.querySelector('input').checked);
    });
  });
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!validateTopic()) {
    topicInput.focus();
    return;
  }

  setLoading(true);
  const payload = {
    topic: topicInput.value.trim(),
    style: document.querySelector('#style').value,
    length: document.querySelector('input[name="length"]:checked').value,
  };

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(await parseError(response));
    const script = await response.json();
    renderScript(script);
    await loadHistory();
    showToast('Your script is ready and saved.');
  } catch (error) {
    loadingState.hidden = true;
    emptyState.hidden = currentScript !== null;
    scriptResult.hidden = currentScript === null;
    showToast(error.message || 'Generation failed. Please try again.', true);
  } finally {
    generateButton.disabled = false;
    generateButton.classList.remove('loading');
    clearInterval(loadingMessageTimer);
  }
});

historyList.addEventListener('click', (event) => {
  const item = event.target.closest('.history-item');
  if (item) openSavedScript(item.dataset.id);
});

document.querySelector('#refresh-history').addEventListener('click', loadHistory);

document.querySelector('#copy-button').addEventListener('click', async () => {
  if (!currentScript) return;
  try {
    await navigator.clipboard.writeText(currentScript.full_script);
    const buttonText = document.querySelector('#copy-button span');
    buttonText.textContent = 'Copied';
    showToast('Full script copied to your clipboard.');
    setTimeout(() => { buttonText.textContent = 'Copy script'; }, 1800);
  } catch {
    showToast('Clipboard access was blocked by the browser.', true);
  }
});

downloadButton.addEventListener('click', (event) => {
  event.stopPropagation();
  const open = downloadMenu.hidden;
  downloadMenu.hidden = !open;
  downloadButton.setAttribute('aria-expanded', String(open));
});

document.addEventListener('click', () => {
  downloadMenu.hidden = true;
  downloadButton.setAttribute('aria-expanded', 'false');
});

downloadMenu.addEventListener('click', (event) => event.stopPropagation());
loadHistory();
