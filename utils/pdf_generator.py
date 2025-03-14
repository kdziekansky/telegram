# utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import cm
import io
import os
import datetime

def generate_conversation_pdf(conversation, user_info, bot_name="AI Bot"):
    """
    Generuje plik PDF z historią konwersacji
    
    Args:
        conversation (list): Lista wiadomości z konwersacji
        user_info (dict): Informacje o użytkowniku
        bot_name (str): Nazwa bota
        
    Returns:
        BytesIO: Bufor zawierający wygenerowany plik PDF
    """
    buffer = io.BytesIO()
    
    # Konfiguracja dokumentu
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Style
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='UserMessage',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        spaceAfter=10,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='BotMessage',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leftIndent=20,
        spaceAfter=14,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=1
    ))
    
    # Elementy dokumentu
    elements = []
    
    # Nagłówek
    elements.append(Paragraph(f"Konwersacja z {bot_name}", styles['Title']))
    
    # Metadane
    current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    metadata_text = f"Data eksportu: {current_time}"
    if user_info.get('username'):
        metadata_text += f" | Użytkownik: {user_info.get('username')}"
    if user_info.get('first_name'):
        name = user_info.get('first_name')
        if user_info.get('last_name'):
            name += f" {user_info.get('last_name')}"
        metadata_text += f" | Imię: {name}"
    
    elements.append(Paragraph(metadata_text, styles['Italic']))
    elements.append(Spacer(1, 0.8*cm))
    
    # Treść konwersacji
    for msg in conversation:
        if msg['is_from_user']:
            icon = "👤 "  # Ikona użytkownika
            style = styles['UserMessage']
            content = f"{icon}Ty: {msg['content']}"
        else:
            icon = "🤖 "  # Ikona bota
            style = styles['BotMessage']
            content = f"{icon}{bot_name}: {msg['content']}"
        
        # Dodaj datę i godzinę wiadomości, jeśli są dostępne
        if 'created_at' in msg and msg['created_at']:
            try:
                # Konwersja formatu daty
                if isinstance(msg['created_at'], str) and 'T' in msg['created_at']:
                    dt = datetime.datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
                    time_str = dt.strftime("%d-%m-%Y %H:%M")
                    content += f"<br/><font size=7 color=gray>{time_str}</font>"
            except Exception as e:
                # Ignoruj błędy konwersji daty
                pass
                
        elements.append(Paragraph(content, style))
    
    # Stopka
    elements.append(Spacer(1, 1.5*cm))
    footer_text = f"Wygenerowano przez {bot_name} • {current_time}"
    elements.append(Paragraph(footer_text, styles['Footer']))
    
    # Wygeneruj dokument
    doc.build(elements)
    
    # Zresetuj pozycję w buforze i zwróć go
    buffer.seek(0)
    return buffer