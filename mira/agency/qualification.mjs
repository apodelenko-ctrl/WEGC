/** Local self-assessment only. No lead score, identity check or admission decision. */
export const MODELS = Object.freeze({
  new_direction: 'Пока нет зарубежного направления — хотим добавить',
  overseas_desk: 'Есть зарубежный отдел',
  thailand_desk: 'Уже работаем с Таиландом',
  network: 'Представляем сеть / франшизу'
});
export const GOALS = Object.freeze({
  client_request: 'Обсудить существующий запрос клиента',
  build_direction: 'Подготовить новое направление',
  improve_process: 'Улучшить отдельный этап работы',
  explore: 'Сначала разобраться в модели'
});
export const OWNERS = Object.freeze({
  decision_maker: 'Владелец / руководитель',
  assigned_manager: 'Есть ответственный менеджер',
  independent_broker: 'Независимый брокер',
  not_assigned: 'Ответственный пока не определён'
});
const scenarios = {
  new_direction: {
    title: 'Новое направление без перестройки агентства',
    description: 'Начните с модели работы и подготовки команды. На первой демонстрации разберите один зарубежный запрос, не весь рынок сразу.',
    first: 'Пройдите стартовый сценарий: проект, роли агентства и МИРА, запрос и отдельное подтверждение застройщика.',
    view: 'onboarding'
  },
  overseas_desk: {
    title: 'Дополнить зарубежный отдел, не заменить его',
    description: 'Сохраните действующую команду и процесс. Выберите, чего именно не хватает: предложения Пхукета, материалов, регистрации или координации сделки.',
    first: 'Сопоставьте конкретный пробел вашего процесса с каталогом и возможностями МИРА.',
    view: 'catalog'
  },
  thailand_desk: {
    title: 'Подключить инфраструктуру к конкретной задаче',
    description: 'Вы уже работаете с рынком. Обсуждение стоит начинать с нужного проекта или этапа сделки, а не с вводной презентации Таиланда.',
    first: 'Выберите этап для разбора: материалы, подтверждение регистрации, статусы сделки или комиссионный контур.',
    view: 'clients'
  },
  network: {
    title: 'Один управляемый пилот для вашей сети',
    description: 'Начните с одной команды и чётких полномочий. Подключение отдельного офиса не означает договорённость со всей сетью.',
    first: 'Определите юридическое лицо, границы пилотной команды и человека, уполномоченного согласовать подключение.',
    view: 'onboarding'
  }
};
const goalSteps = {
  client_request: 'Подготовьте описание задачи по одному проекту, без имени, контактов и документов покупателя. Реальная регистрация возможна только после допуска проекта и согласований.',
  build_direction: 'Определите первый клиентский сценарий и материалы, которые понадобятся вашей команде для консультации.',
  improve_process: 'Выберите один этап, который требует улучшения, и сформулируйте ожидаемый результат обсуждения.',
  explore: 'Откройте демо и стартовый комплект. Не создавайте реальную клиентскую заявку ради знакомства с продуктом.'
};
const ownerSteps = {
  decision_maker: 'Зафиксируйте, кто будет ежедневно вести новое направление и следующий шаг с клиентом.',
  assigned_manager: 'Подготовьте ответственного менеджера к демонстрации и уточните, кто согласует договор и доступ.',
  independent_broker: 'Согласуйте вашу договорную роль и полномочия до рабочего подключения; статус брокера не создаёт автоматический допуск.',
  not_assigned: 'Сначала определите ответственного за направление и человека, который согласует подключение. До этого начните с демо.'
};
export function validModel(value) {
  return typeof value === 'string' && Object.hasOwn(MODELS, value);
}
export function createPlan(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new TypeError('Выберите ответы на все три вопроса.');
  for (const [field, options] of [['model', MODELS], ['goal', GOALS], ['owner', OWNERS]]) {
    if (!Object.hasOwn(input, field) || typeof input[field] !== 'string' || !Object.hasOwn(options, input[field])) {
      throw new TypeError('Выберите ответы на все три вопроса.');
    }
  }
  const s = scenarios[input.model];
  const steps = [s.first, goalSteps[input.goal], ownerSteps[input.owner]];
  if (input.owner === 'not_assigned') steps.unshift(steps.pop());
  return {
    title: s.title,
    description: s.description,
    answers: { model: MODELS[input.model], goal: GOALS[input.goal], owner: OWNERS[input.owner] },
    steps,
    demoUrl: `/mira/marketplace.html?view=${s.view}`,
    boundary: 'Это предварительный сценарий по вашим ответам, не проверка агентства и не одобрение пилота. Договор, доступ и правила конкретного проекта согласовываются отдельно.',
    submitted: false,
    approved: false
  };
}
export function briefText(input) {
  const p = createPlan(input);
  return [
    'МИРА — бриф для обсуждения подключения',
    'Локальный черновик. Не отправлен. Не подтверждает доступ или регистрацию клиента.',
    '', 'Модель агентства: ' + p.answers.model, 'Задача: ' + p.answers.goal,
    'Ответственный: ' + p.answers.owner, '', p.title, p.description, '',
    ...p.steps.map((step, i) => `${i + 1}. ${step}`), '', p.boundary,
    '', 'Страница: https://wegc.fund/mira/agency/',
    'Демо: https://wegc.fund' + p.demoUrl, '',
    'Клиентские данные, документы, цены и комиссии в этот бриф не включены.'
  ].join('\n') + '\n';
}
