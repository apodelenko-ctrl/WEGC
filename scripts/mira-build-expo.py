#!/usr/bin/env python3
"""Original vector exhibition concept, exact QR, no external images or fonts shipped."""
from pathlib import Path
import json,hashlib,html
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'mira/expo';TARGET='https://wegc.fund/mira/start/'

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    qr=qrcode.QRCode(error_correction=ERROR_CORRECT_Q,box_size=10,border=4);qr.add_data(TARGET);qr.make(fit=True);matrix=qr.get_matrix();n=len(matrix)
    d=' '.join(f'M{x} {y}h1v1h-1z'for y,row in enumerate(matrix)for x,on in enumerate(row)if on)
    standalone=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" width="740" height="740"><title>QR: {html.escape(TARGET)}</title><rect width="{n}" height="{n}" fill="white"/><path d="{d}" fill="#171b20"/></svg>'
    (OUT/'qr.svg').write_text(standalone);qr.make_image(fill_color='#171b20',back_color='white').save(OUT/'qr.png')
    scale=242/n
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="850mm" height="2000mm" viewBox="0 0 850 2000"><title>МИРА — Пхукет в вашем агентстве</title><rect width="850" height="2000" fill="#171b20"/><path d="M0 0H850V22H0Z" fill="#ee4338"/><g font-family="Arial,DejaVu Sans,sans-serif" fill="white"><text x="65" y="118" font-size="66" font-weight="bold" letter-spacing="-4">МИРА</text><path d="M264 114L298 80M269 80H298V109" fill="none" stroke="#ff655d" stroke-width="7"/><text x="65" y="178" font-size="20" letter-spacing="3">ДЛЯ АГЕНТСТВ НЕДВИЖИМОСТИ</text><text x="65" y="310" font-size="80" font-weight="bold" letter-spacing="-3">ВАШ КЛИЕНТ</text><text x="65" y="408" font-size="80" font-weight="bold" letter-spacing="-3">ХОЧЕТ</text><text x="65" y="512" font-size="98" font-weight="bold" letter-spacing="-4" fill="#ff655d">ПХУКЕТ?</text><text x="65" y="591" font-size="33">Не отдавайте зарубежный запрос.</text><text x="65" y="637" font-size="33">Добавьте новое направление.</text></g><path d="M290 1260V903A168 168 0 0 1 626 903V1260Z" fill="#97c3c0" stroke="#ef493f" stroke-width="24"/><path d="M302 1008Q451 935 614 1010V1248H302Z" fill="#f1eee1"/><path d="M302 1090Q460 1030 614 1070V1190Q460 1160 302 1205Z" fill="#448883"/><path d="M302 1248V903Q302 750 470 735L401 865V1281Z" fill="#e8352d" stroke="#ff7067" stroke-width="3"/><path d="M374 1065V1105" stroke="white" stroke-width="7" stroke-linecap="round"/><path d="M260 1290H660" stroke="#4b5158" stroke-width="3"/><g font-family="Arial,DejaVu Sans,sans-serif" fill="white"><text x="65" y="1408" font-size="39" font-weight="bold">Ваш клиент. Ваш бренд.</text><text x="65" y="1466" font-size="33" fill="#cdd4d8">Международная поддержка МИРА.</text><text x="350" y="1622" font-size="28" font-weight="bold">ОТКРОЙТЕ КАТАЛОГ</text><text x="350" y="1664" font-size="28" font-weight="bold">И МОДЕЛЬ РАБОТЫ</text><text x="350" y="1730" font-size="22" fill="#cdd4d8">Начните с Пхукета.</text><text x="350" y="1769" font-size="22" fill="#cdd4d8">Без переезда вашего агентства.</text><text x="65" y="1880" font-size="29">wegc.fund/mira/start/</text><text x="65" y="1935" font-size="15" fill="#b5bec4">Каталог для знакомства. Наличие и условия проекта подтверждаются отдельно.</text></g><g transform="translate(65 1550) scale({scale})"><rect width="{n}" height="{n}" fill="white"/><path d="{d}" fill="#171b20"/></g></svg>'''
    (OUT/'banner.svg').write_text(svg)
    # PDF from the same original SVG, not a raster placed in a PDF.
    import cairosvg
    cairosvg.svg2pdf(bytestring=svg.encode(),write_to=str(OUT/'banner.pdf'))
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/'banner.png'),output_width=850,output_height=2000)
    record={'target':TARGET,'status':'concept_for_owner_approval','print_size':'850x2000 mm proposed; confirm with printer','error_correction':'Q','quiet_zone_modules':4,'external_images':False,'owner_approved':False}
    (OUT/'qr-check.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':build()
