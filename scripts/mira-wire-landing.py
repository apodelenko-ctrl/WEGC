#!/usr/bin/env python3
"""Small idempotent integration of the accepted landing; no marketing rewrite."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
MARKER='<!-- MIRA-INTAKE-GATE v1 -->'
PUBLIC_MARKER='<!-- MIRA-PUBLIC-INTAKE v2 -->'
def transform(source):
    source=source.replace('Оставьте рабочий контакт и задачу —','Оставьте рабочий контакт —')
    if PUBLIC_MARKER in source:return source
    if MARKER in source:
        replacement=PUBLIC_MARKER+'<div class="pilot-entry"><p>Публичный приём заявок агентств открыт. Оставьте рабочий контакт — команда МИРА ответит на рабочий email.</p><p><a class="btn" href="https://pilot.wegc.fund/mira/request/">Подать заявку агентства</a></p><p class="fine">Приглашение не требуется. Данные покупателей не нужны. Договор и условия работы согласуются отдельно.</p><p><a href="./pilot.html">Вход по уже выданному приглашению</a></p></div>'
        source,n=re.subn(re.escape(MARKER)+r'<div class="pilot-entry">.*?</div>',lambda _:replacement,source,count=1,flags=re.S)
        if n!=1:raise ValueError('Expected one existing pilot entry')
        source=source.replace('Рабочая заявка принимается только через защищённый доступ и подтверждается серверным номером.','Оставьте заявку — мы свяжемся с вами по рабочему email.')
        return source
    button='<a class="btn" href="#join">Запросить демонстрацию</a>'
    if source.count(button)!=1 or source.count('<form onsubmit="sendLead(event)">')!=1:
        raise ValueError('Landing structure changed: review before modifying')
    source=source.replace(button,'<a class="btn" href="./marketplace.html">Открыть демонстрационный кабинет</a><p class="fine">Демо: без реальных клиентских данных и отправки заявок.</p>')
    source=source.replace('Оставьте рабочий контакт. Для пилотной волны подключения обрабатываются вручную.','Начните с демонстрации и брифа агентства. Рабочая заявка принимается только через защищённый доступ и подтверждается серверным номером.')
    replacement=MARKER+'''<div class="pilot-entry"><p>Демонстрация доступна без регистрации. В ней можно проверить каталог и путь клиентского запроса, не передавая персональные данные.</p><p><a class="btn" href="./marketplace.html?view=application">Подготовить бриф агентства</a></p><p><a class="btn" href="./pilot.html">Перейти в закрытый пилот</a></p><p class="fine">Закрытый пилот требует настроенного серверного доступа и подтверждения оператора. Подготовленный бриф не считается отправленной заявкой. Доступ к проекту не означает подтверждённую регистрацию клиента.</p></div>'''
    source,n=re.subn(r'<form onsubmit="sendLead\(event\)">.*?</form>',lambda _:replacement,source,count=1,flags=re.S)
    if n!=1:raise ValueError('Expected exactly one legacy form')
    source,n=re.subn(r'<script>\s*function val\(id\).*?function sendLead\(e\).*?</script>','',source,count=1,flags=re.S)
    if n!=1:raise ValueError('Expected only the known legacy mailto script')
    if 'mailto:post@wegc.fund' in source:raise ValueError('Legacy mailto unexpectedly remains')
    return transform(source)
if __name__=='__main__':
    target=ROOT/'mira/index.html';target.write_text(transform(target.read_text(encoding='utf-8')),encoding='utf-8');print('MIRA landing: demo + fail-closed pilot entry integrated')
