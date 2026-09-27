import { createPlan, validModel } from './qualification.mjs';

const form = document.querySelector('#qualification');
const fields = document.querySelector('#qualification-fields');
const result = document.querySelector('#plan');
const message = document.querySelector('#form-message');
let current = null;
function invalidate() {
  current = null;
  result.hidden = true;
  message.textContent = '';
}
function buildPlan() {
  if (!form.reportValidity()) return;
  const input = Object.fromEntries(new FormData(form));
  try {
    const plan = createPlan(input);
    document.querySelector('#plan-title').textContent = plan.title;
    document.querySelector('#plan-description').textContent = plan.description;
    const list = document.querySelector('#plan-steps');
    list.replaceChildren(...plan.steps.map(text => {
      const item = document.createElement('li');
      item.textContent = text;
      return item;
    }));
    document.querySelector('#plan-demo').href = plan.demoUrl;
    document.querySelector('#plan-boundary').textContent = plan.boundary;
    current = input;
    result.hidden = false;
    message.textContent = 'Сценарий подготовлен. Ничего не отправлено.';
    document.querySelector('#plan-title').focus();
  } catch {
    invalidate();
    message.textContent = 'Не удалось подготовить сценарий. Выберите варианты из списка.';
  }
}
// Prevent keyboard/default form submission as well as explicit button submission.
form.addEventListener('submit', event => { event.preventDefault(); buildPlan(); });
form.addEventListener('change', invalidate);
document.querySelector('#build-plan').addEventListener('click', buildPlan);
document.querySelectorAll('[data-model]').forEach(link => {
  link.addEventListener('click', () => {
    if (validModel(link.dataset.model)) {
      form.elements.model.value = link.dataset.model;
      invalidate();
    }
  });
});
// Only a fixed segment enum is read. Ignore UTM, contact and arbitrary query data.
const segment = new URLSearchParams(window.location.search).get('segment');
if (validModel(segment)) form.elements.model.value = segment;

// Enabled only after every no-send event handler is installed. Static links also work without JS.
fields.disabled = false;
