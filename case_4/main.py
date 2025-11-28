"""
🚀 AI-Business Analyst | ForteBank Hackathon
Generating comprehensive Business Requirement Documents (BRD) from simple ideas.

STACK: Python, Streamlit, OpenAI GPT-4o
"""

import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime

# ==========================================
# 1. CONFIG & STYLES
# ==========================================
st.set_page_config(page_title="AI-Business Analyst", page_icon="💼", layout="wide")

st.markdown("""
<style>
    .report-view { background-color: #f9f9f9; padding: 30px; border-radius: 10px; border: 1px solid #ddd; font-family: 'Segoe UI', serif; }
    .header-style { color: #8e1b3e; font-weight: bold; }
    .sub-header { color: #333; margin-top: 20px; }
    .stTextArea textarea { font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIC: DOC GENERATOR
# ==========================================
def generate_brd(api_key, project_name, problem, stakeholders):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Ты — Senior Business Analyst в ForteBank (банковский сектор).
    Твоя задача — составить профессиональный документ Бизнес-Требований (BRD).
    
    Входные данные:
    - Проект: {project_name}
    - Проблема/Идея: {problem}
    - Стейкхолдеры: {stakeholders}
    
    Структура документа (используй Markdown):
    # {project_name} - Business Requirements Document
    
    ## 1. Executive Summary
    (Краткое описание сути и целей проекта, бизнес-ценность)
    
    ## 2. Problem Statement
    (Какую боль решаем, текущее состояние AS-IS)
    
    ## 3. Scope of Work
    (Что входит в скоуп, что НЕ входит)
    
    ## 4. User Personas
    (Таблица или список: Роль, Описание, Потребности)
    
    ## 5. Functional Requirements
    (Список требований. Формат: ID | Requirement | Priority MoSCoW)
    
    ## 6. User Stories
    (3-5 ключевых историй в формате "As a... I want to... So that...")
    
    ## 7. Non-Functional Requirements
    (Безопасность, Производительность, Нагрузка - критично для банка)
    
    ## 8. KPI & Success Metrics
    (Как будем измерять успех)
    
    Будь конкретен, используй профессиональный банковский лексикон.
    """
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert Business Analyst. Output clean Markdown."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def create_download_link(content, filename):
    # Оборачиваем Markdown в простой HTML для красивого открытия в Word/Браузере
    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Calibri, sans-serif; padding: 40px; line-height: 1.6; }}
        h1 {{ color: #8e1b3e; border-bottom: 2px solid #8e1b3e; }}
        h2 {{ color: #333; margin-top: 30px; background: #f0f0f0; padding: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
    {markdown_to_html_approx(content)}
    </body>
    </html>
    """
    b64 = base64.b64encode(html.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}.html" class="stButton">📥 Скачать официальный отчет (.html)</a>'

def markdown_to_html_approx(md_text):
    # Простейший конвертер для демо (чтобы не тянуть зависимости типа markdown2)
    html = md_text.replace("\n", "<br>")
    html = html.replace("## ", "<h2>").replace("</h2><br>", "</h2>")
    html = html.replace("# ", "<h1>").replace("</h1><br>", "</h1>")
    html = html.replace("**", "<b>")
    return html

# ==========================================
# 3. UI LAYOUT
# ==========================================
with st.sidebar:
    st.title("💼 AI-BA Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    st.info("💡 **Совет:** Выберите шаблон ниже, чтобы не придумывать текст.")
    
    template = st.radio("Шаблоны:", ["Свой вариант", "Мобильная ипотека", "Антифрод система", "HR-портал"])
    
    prefill_project = ""
    prefill_problem = ""
    prefill_stakeholders = ""
    
    if template == "Мобильная ипотека":
        prefill_project = "Forte Mortgage Mobile Flow"
        prefill_problem = "Клиенты жалуются, что оформление ипотеки требует 5 визитов в отделение. Процесс непрозрачен. Конкуренты выдают решения за 1 день."
        prefill_stakeholders = "Департамент ипотечного кредитования, IT-департамент, Клиенты, Риски."
    elif template == "Антифрод система":
        prefill_project = "Transaction Shield AI"
        prefill_problem = "Рост мошеннических транзакций P2P. Текущие правила (rule-based) дают много ложных срабатываний и блокируют честных клиентов."
        prefill_stakeholders = "Security Team, Compliance, Операционный блок."

st.title("🤖 AI-Business Analyst")
st.markdown("##### Ваш цифровой помощник для создания бизнес-требований (BRD) за 1 минуту.")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("1. Интервью")
    with st.form("ba_form"):
        project_name = st.text_input("Название проекта", value=prefill_project)
        problem_desc = st.text_area("Опишите проблему или идею", height=150, value=prefill_problem, help="Какую боль решаем? Что хотим получить?")
        stakeholders = st.text_area("Ключевые стейкхолдеры", height=80, value=prefill_stakeholders)
        
        submitted = st.form_submit_button("🚀 Сгенерировать документацию", type="primary")

if submitted:
    with col2:
        if not api_key:
            st.error("❌ Введите API Key!")
        else:
            with st.status("🧠 AI Анализирует вводные данные...", expanded=True) as status:
                st.write("Формирование структуры документа...")
                st.write("Определение User Personas...")
                st.write("Написание функциональных требований...")
                
                try:
                    # ГЕНЕРАЦИЯ
                    doc_content = generate_brd(api_key, project_name, problem_desc, stakeholders)
                    
                    status.update(label="✅ Документ готов!", state="complete", expanded=False)
                    
                    # ОТОБРАЖЕНИЕ
                    st.subheader("2. Результат (Draft)")
                    
                    # Кнопка скачивания
                    st.markdown(create_download_link(doc_content, f"BRD_{project_name.replace(' ', '_')}"), unsafe_allow_html=True)
                    
                    # Предпросмотр в красивом блоке
                    st.markdown(f'<div class="report-view">{doc_content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Ошибка: {e}")

# Пустое состояние справа
if not submitted:
    with col2:
        st.info("👈 Заполните форму слева и нажмите кнопку, чтобы увидеть магию AI.")
        st.markdown("""
        **Что сгенерирует AI:**
        1. Executive Summary
        2. AS-IS vs TO-BE анализ
        3. Таблицу User Personas
        4. Список User Stories
        5. Нефункциональные требования (Security, Load)
        6. KPI проекта
        """)