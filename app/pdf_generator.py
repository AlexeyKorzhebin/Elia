"""Генератор PDF отчетов о приеме"""
from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

# Регистрируем шрифты DejaVu для поддержки кириллицы
# DejaVu шрифты поставляются вместе с reportlab
try:
    # Пробуем использовать системные шрифты или шрифты из reportlab
    from reportlab.pdfbase.pdfmetrics import registerFont
    
    # Для macOS и Linux можно использовать системные шрифты
    # Для Windows путь может отличаться
    font_paths = {
        'regular': [
            '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
        ],
        'bold': [
            '/System/Library/Fonts/Supplemental/Arial Bold.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
            'C:\\Windows\\Fonts\\arialbd.ttf',  # Windows
        ]
    }
    
    # Пытаемся найти подходящие шрифты
    font_registered = False
    regular_font = None
    bold_font = None
    
    # Ищем regular шрифт
    for font_path in font_paths['regular']:
        if os.path.exists(font_path):
            regular_font = font_path
            break
    
    # Ищем bold шрифт
    for font_path in font_paths['bold']:
        if os.path.exists(font_path):
            bold_font = font_path
            break
    
    # Регистрируем шрифты, если нашли
    if regular_font and bold_font:
        try:
            pdfmetrics.registerFont(TTFont('CustomFont', regular_font))
            pdfmetrics.registerFont(TTFont('CustomFont-Bold', bold_font))
            font_registered = True
            FONT_NAME = 'CustomFont'
            FONT_NAME_BOLD = 'CustomFont-Bold'
        except Exception as e:
            print(f"Failed to register fonts: {e}")
            font_registered = False
    
    # Если не нашли системный шрифт, используем встроенный Helvetica
    if not font_registered:
        FONT_NAME = 'Helvetica'
        FONT_NAME_BOLD = 'Helvetica-Bold'
        
except Exception as e:
    print(f"Font registration error: {e}")
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'


def generate_appointment_pdf(appointment_data: dict, patient_data: dict, report_data: dict = None) -> BytesIO:
    """
    Генерирует PDF с информацией о приеме
    
    Args:
        appointment_data: Данные о приеме
        patient_data: Данные о пациенте
        report_data: Данные медицинского отчета (опционально)
    
    Returns:
        BytesIO: Поток с PDF документом
    """
    buffer = BytesIO()
    
    # Создаем документ
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Создаем стили
    styles = getSampleStyleSheet()
    
    # Создаем кастомные стили для русского текста с поддержкой кириллицы
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME_BOLD,
        fontSize=18,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME_BOLD,
        fontSize=14,
        textColor=colors.HexColor('#1A1A1A'),
        spaceAfter=10,
        spaceBefore=15,
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#666666'),
    )
    
    # Элементы документа
    elements = []
    
    # Заголовок
    elements.append(Paragraph("Медицинский отчет о приеме", title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Информация о пациенте
    elements.append(Paragraph("Информация о пациенте", heading_style))
    
    patient_info = [
        ['ФИО:', patient_data.get('full_name', 'Не указано')],
        ['Пол:', 'Мужской' if patient_data.get('gender') == 'male' else 'Женский'],
        ['Возраст:', str(patient_data.get('age', 'Не указан'))],
        ['Дата рождения:', patient_data.get('date_of_birth', 'Не указана')],
        ['МО прикрепления:', patient_data.get('medical_organization', 'Не указано')],
        ['Участок:', patient_data.get('medical_area', 'Не указан')],
    ]
    
    patient_table = Table(patient_info, colWidths=[5*cm, 12*cm])
    patient_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), FONT_NAME_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Хронические заболевания
    if patient_data.get('chronic_diseases'):
        elements.append(Paragraph("Хронические заболевания", heading_style))
        for disease in patient_data['chronic_diseases']:
            elements.append(Paragraph(f"• {disease['name']}", normal_style))
        elements.append(Spacer(1, 0.3*cm))
    
    # Последние заболевания
    if patient_data.get('recent_diseases'):
        elements.append(Paragraph("Последние заболевания", heading_style))
        for disease in patient_data['recent_diseases']:
            elements.append(Paragraph(f"• {disease['name']}", normal_style))
        elements.append(Spacer(1, 0.3*cm))
    
    # Показатели здоровья
    health_indicators = patient_data.get('health_indicators')
    if health_indicators:
        elements.append(Paragraph("Показатели здоровья", heading_style))
        
        health_data = []
        if health_indicators.get('hemoglobin'):
            health_data.append(['Гемоглобин:', f"{health_indicators['hemoglobin']} г/л"])
        if health_indicators.get('cholesterol'):
            health_data.append(['Холестерин:', f"{health_indicators['cholesterol']} ммоль/л"])
        if health_indicators.get('bmi'):
            health_data.append(['ИМТ:', f"{health_indicators['bmi']} кг/м²"])
        if health_indicators.get('heart_rate'):
            health_data.append(['ЧСС:', f"{health_indicators['heart_rate']} уд/мин"])
        
        if health_data:
            health_table = Table(health_data, colWidths=[5*cm, 12*cm])
            health_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), FONT_NAME_BOLD),
                ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ]))
            elements.append(health_table)
            elements.append(Spacer(1, 0.5*cm))
    
    # Информация о приеме
    elements.append(Paragraph("Информация о приеме", heading_style))
    
    appointment_info = [
        ['Дата:', appointment_data.get('appointment_date', 'Не указана')],
        ['Время:', f"{appointment_data.get('appointment_time_start', '')}–{appointment_data.get('appointment_time_end', '')}"],
        ['Статус:', appointment_data.get('status', 'Не указан')],
    ]
    
    appointment_table = Table(appointment_info, colWidths=[5*cm, 12*cm])
    appointment_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, -1), FONT_NAME_BOLD),
        ('FONTNAME', (1, 0), (1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
    ]))
    elements.append(appointment_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Медицинский отчет (если есть)
    if report_data:
        elements.append(Paragraph("Медицинский отчет", heading_style))
        
        if report_data.get('purpose'):
            elements.append(Paragraph("Цель обращения:", label_style))
            elements.append(Paragraph(report_data['purpose'], normal_style))
            elements.append(Spacer(1, 0.3*cm))
        
        if report_data.get('complaints'):
            elements.append(Paragraph("Жалобы пациента:", label_style))
            elements.append(Paragraph(report_data['complaints'], normal_style))
            elements.append(Spacer(1, 0.3*cm))
        
        if report_data.get('anamnesis'):
            elements.append(Paragraph("Анамнез:", label_style))
            elements.append(Paragraph(report_data['anamnesis'], normal_style))
            elements.append(Spacer(1, 0.3*cm))
        
        if report_data.get('submitted_to_mis'):
            success_style = ParagraphStyle(
                'Success',
                parent=normal_style,
                fontName=FONT_NAME,
                textColor=colors.HexColor('#059669'),
            )
            elements.append(Paragraph(
                f"Отчет отправлен в МИС: {report_data.get('submitted_at', '')}",
                success_style
            ))
    
    # Генерируем PDF
    doc.build(elements)
    
    # Возвращаем в начало потока
    buffer.seek(0)
    return buffer

