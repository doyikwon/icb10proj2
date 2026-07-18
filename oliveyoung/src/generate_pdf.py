"""
올리브영 영양제 시장 분석 마크다운 보고서(EDA_Report.md)와 생성된 시각화 차트 이미지들을 활용하여,
맑은 고딕(Malgun Gothic) 한글 폰트가 적용된 고품질 PDF 보고서(EDA_Report.pdf)를 자동 빌드하는 스크립트입니다.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def build_pdf():
    pdf_path = "oliveyoung/report/EDA_Report.pdf"
    md_path = "oliveyoung/report/EDA_Report.md"
    
    if not os.path.exists(md_path):
        print(f"마크다운 보고서가 존재하지 않습니다: {md_path}")
        return

    # 1. 맑은 고딕 한글 폰트 등록
    font_path = "C:\\Windows\\Fonts\\malgun.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\malgunbd.ttf"
    
    if not os.path.exists(font_path):
        # 맑은 고딕이 없을 경우 기본 돋움이나 시스템 폰트 탐색 (안전장치)
        font_path = "C:\\Windows\\Fonts\\gulim.ttc"
        font_bold_path = "C:\\Windows\\Fonts\\gulim.ttc"
        
    pdfmetrics.registerFont(TTFont('KoreanRegular', font_path))
    pdfmetrics.registerFont(TTFont('KoreanBold', font_bold_path))

    # 2. 스타일 정의
    styles = getSampleStyleSheet()
    
    # 기본 폰트를 한글 폰트로 교체한 스타일 신규 추가
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='KoreanBold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading1'],
        fontName='KoreanBold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#16A085'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='KoreanBold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2980B9'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='KoreanRegular',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=8
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='KoreanRegular',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#2C3E50')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='KoreanBold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    story = []
    
    # 3. 마크다운 파싱 및 빌드
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    in_table = False
    table_data = []
    
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        
        # 테이블 파싱
        if line_strip.startswith("|"):
            in_table = True
            # 구분선(---) 라인은 스킵
            if "---" in line_strip:
                continue
            # 셀 파싱 및 공백 제거
            cells = [c.strip() for c in line_strip.split("|")[1:-1]]
            table_data.append(cells)
            continue
        elif in_table:
            # 테이블 영역이 끝나면 객체 생성하여 story에 추가
            if table_data:
                formatted_table_data = []
                for row_idx, row in enumerate(table_data):
                    formatted_row = []
                    for cell in row:
                        cell_style = table_header_style if row_idx == 0 else table_cell_style
                        formatted_row.append(Paragraph(cell, cell_style))
                    formatted_table_data.append(formatted_row)
                
                # 표 스타일 지정
                t = Table(formatted_table_data, hAlign='LEFT')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16A085')),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('LEFTPADDING', (0,0), (-1,-1), 5),
                    ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t)
                story.append(Spacer(1, 10))
                
            in_table = False
            table_data = []
            
        if not line_strip:
            continue
            
        # 제목 및 헤더 처리
        if line_strip.startswith("# "):
            story.append(Paragraph(line_strip[2:], title_style))
            story.append(Spacer(1, 10))
        elif line_strip.startswith("## "):
            story.append(Paragraph(line_strip[3:], h1_style))
            story.append(Spacer(1, 5))
        elif line_strip.startswith("### "):
            story.append(Paragraph(line_strip[4:], h2_style))
            story.append(Spacer(1, 4))
        # 이미지 태그 처리
        elif line_strip.startswith("![") or (line_strip.startswith("![]") or "plot" in line_strip):
            # 이미지 파일명 추출 (예: plot1_orig_price_dist.png)
            match = re.search(r'plot\w+\.png', line_strip)
            if match:
                img_name = match.group(0)
                img_path = f"oliveyoung/images/{img_name}"
                if os.path.exists(img_path):
                    # 보고서 가독성을 위해 적절한 크기로 이미지 삽입
                    story.append(Image(img_path, width=420, height=260, hAlign='LEFT'))
                    story.append(Spacer(1, 10))
        # 일반 본문 처리
        else:
            # 마크다운 굵게 표시(**) 등을 간단히 HTML 태그로 치환
            cleaned_text = line_strip.replace("**", "<b>", 1).replace("**", "</b>", 1)
            # 글머리 기호(*) 치환
            if cleaned_text.startswith("* "):
                cleaned_text = "&bull; " + cleaned_text[2:]
            elif cleaned_text.startswith("- "):
                cleaned_text = "&bull; " + cleaned_text[2:]
                
            story.append(Paragraph(cleaned_text, body_style))
            story.append(Spacer(1, 4))
            
    # PDF 빌드 실행
    doc.build(story)
    print(f"성공적으로 {pdf_path}를 빌드하였습니다.")

if __name__ == "__main__":
    build_pdf()
