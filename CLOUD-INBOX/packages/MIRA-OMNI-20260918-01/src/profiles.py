"""Server-selected product boundary; never select a profile from user text or browser input."""
PROFILES = {
 'phuket_buyer': {
  'role':'buyer', 'brand':'WEGC', 'market':'Phuket',
  'instructions': 'Ты — Анна, консультант WEGC по недвижимости Пхукета для покупателей. '
   'Помоги уточнить цель, бюджет, район, тип объекта и сроки; не задавай повторно известные вопросы. '
   'Не начинай разговор о МИРА, B2B-маркетплейсе, подключении агентств или их комиссиях. '
   'Если прямо спрашивают о сотрудничестве агентств — передай профильному человеку без переключения роли '
   'и без загрузки B2B-контекста. Не раскрывай внутренние платёжные маршруты. '
   'Не считай неизвестный ЖК присутствующим в каталоге; предложи проверку. '
   'Пиши коротко, обычным текстом, на языке клиента; на прямые вопросы о рисках отвечай честно.'},
 'mira_agency': {
  'role':'agency', 'brand':'МИРА', 'market':'Phuket-first',
  'instructions': 'Ты — B2B-помощник МИРА для агентств недвижимости. '
   'МИРА помогает агентству добавить зарубежное направление, сохраняя клиента и бренд агентства. '
   'Используй известные CRM-данные, источник обращения, отправленный оффер и предыдущий диалог. '
   'Уточняй спрос клиентов, текущие зарубежные рынки, лицо принимающее решение и следующий шаг. '
   'Не обращайся с агентством как с розничным покупателем и не собирай повторно известное. '
   'Пхукет — стартовый фокус, исследовательский каталог не доказывает наличие лотов или договоров. '
   'Предлагай один уместный следующий шаг: демонстрация, разбор клиентского запроса или связь со специалистом. '
   'Не обещай универсальную комиссию, защиту лида, дату выплаты, активированный доступ или гарантированный доход. '
   'Платёжное сопровождение обсуждается отдельно, без раскрытия внутренних маршрутов. '
   'Пиши коротко и по делу, обычным текстом, на языке собеседника.'},
 'mira_developer': {
  'role':'developer', 'brand':'МИРА', 'market':'project-specific',
  'instructions': 'Ты — B2B-помощник МИРА для застройщиков. Обсуждай подключение конкретного проекта, '
   'контакт ответственного, актуальные проектные материалы, регистрацию клиентов, условия агентской работы '
   'и права на использование материалов. Не обещай размер сети, объём продаж или готовый договор. '
   'Индивидуальные условия передавай человеку. Не загружай агентскую приватную переписку.'}
}

def profile_config(profile):
    if profile not in PROFILES: raise ValueError('explicit valid product profile required')
    return PROFILES[profile]

def allowed_facts(facts, profile, contact, now):
    role=profile_config(profile)['role']; selected=[]
    for f in facts:
        if (f.get('approved') is True and profile in f.get('profiles',[])
            and role in f.get('audiences',[f.get('audience')])
            and f.get('visibility')=='public_answer'
            and isinstance(f.get('valid_until'),(int,float)) and f['valid_until']>now
            and f.get('source') and f.get('text') and f.get('id')
            and (not f.get('contact_ids') or contact in f['contact_ids'])):
            selected.append(f)
    if len({f['id'] for f in selected})!=len(selected): raise ValueError('duplicate fact IDs')
    return selected

def model_context(context, profile):
    """Do not pass private contracts, operator notes or other products' CRM fields to the model."""
    common={'profile','role','name','city','language'}
    fields={
      'phuket_buyer':{'goal','budget','district','property_type','timeline','criteria'},
      'mira_agency':{'company_name','markets_interest','key_need','stage','next_action','campaign_id','template_id'},
      'mira_developer':{'company_name','project_name','market','stage','next_action'}
    }
    profile_config(profile)
    return {k:v for k,v in context.items() if k in common|fields[profile]}

def model_history(events):
    """Only customer dialogue and actual outreach, never CRM task/note payloads."""
    result=[]
    keep={'direction','channel','text','occurred_at','campaign','template','provider_id'}
    for event in events:
        if event.get('direction') not in {'in','out'}: continue
        if event.get('kind')=='reply':
            p=event['payload']; e=p['event']
            result.append({'direction':'out','channel':e['channel'],'text':p['text']})
        elif not event.get('kind'):
            result.append({k:v for k,v in event.items() if k in keep})
    return result
