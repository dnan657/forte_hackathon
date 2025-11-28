"""
🚀 AI-Procure: Intelligent Tender Analysis System
🏆 Solution for ForteBank AI Hackathon

AUTHOR: [Your Team Name]
STACK: Python, Streamlit, OpenAI GPT-4o, Pydantic

HOW TO RUN:
1. pip install streamlit openai pydantic
2. streamlit run main.py
"""

import streamlit as st
import json
import time
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

# ==========================================
# 1. CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="AI-Procure | ForteBank", page_icon="🛡️", layout="wide")

# Custom CSS for "Professional Bank Look"
st.markdown("""
<style>
    /* Main container tweaks */
    .block-container { padding-top: 2rem; }
    
    /* Risk Badges */
    .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9em; }
    .badge-high { background-color: #ffcccc; color: #cc0000; border: 1px solid #cc0000; }
    .badge-medium { background-color: #fff4cc; color: #996600; border: 1px solid #996600; }
    .badge-low { background-color: #ccffcc; color: #006600; border: 1px solid #006600; }
    
    /* Metrics */
    .metric-box { border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; text-align: center; background: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .metric-val { font-size: 1.5em; font-weight: bold; color: #8e1b3e; } /* Forte Redish color */
    .metric-lbl { color: #666; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA MODELS (STRUCTURED OUTPUT)
# ==========================================
class RiskFactor(BaseModel):
    category: str = Field(..., description="Категория: Сроки, Цена, Аффилированность, ТЗ, Юр.риски")
    severity: str = Field(..., description="Уровень риска: HIGH, MEDIUM, LOW")
    description: str = Field(..., description="Краткое описание проблемы")

class TenderAnalysis(BaseModel):
    summary: str = Field(..., description="Краткая суть тендера (1-2 предложения)")
    extracted_budget: str = Field(..., description="Бюджет с валютой")
    extracted_deadline: str = Field(..., description="Сроки поставки/выполнения")
    risk_score: int = Field(..., description="Оценка риска от 0 (безопасно) до 100 (критично)")
    risk_factors: List[RiskFactor]
    recommendation: str = Field(..., description="Вердикт: ОДОБРИТЬ, ТРЕБУЕТ ПРОВЕРКИ, ОТКЛОНИТЬ")
    reasoning: str = Field(..., description="Обоснование вердикта для менеджера")

# ==========================================
# 3. TEST DATA (EMBEDDED)
# ==========================================
CASES = {
    "clean": {
        "label": "✅ Чистый кейс (Канцелярия)",
        "text": """
        ТЕНДЕРНАЯ ДОКУМЕНТАЦИЯ № 102/2025
        Заказчик: АО "Городские Сети"
        Предмет закупки: Бумага офисная А4, класс C.
        Объем: 2000 пачек.
        Бюджет: 4 500 000 тенге (с НДС).
        Технические спецификации: Белизна 146% CIE, плотность 80 г/м2. Соответствие ГОСТ Р 57641-2017.
        Срок поставки: 15 рабочих дней с момента подписания договора.
        Условия оплаты: По факту поставки в течение 30 календарных дней.
        Требования к поставщику: Отсутствие в реестре недобросовестных поставщиков.
        """
    },
    "corruption": {
        "label": "⛔️ Коррупционный кейс (Ноутбуки)",
        "text": """
        Лот № 777-VIP. Поставка вычислительной техники для нужд Департамента.
        Предмет: Портативный компьютер (Ноутбук) - 10 штук.
        Бюджет: 35 000 000 тенге.
        
        Техническая спецификация (строгое соответствие):
        1. Процессор: Intel Core i9-13980HX (не ниже).
        2. Цвет корпуса: "Space Gray" с гравировкой логотипа поставщика.
        3. Вес: ровно 2.15 кг (отклонение не допускается).
        4. Предустановленное ПО: WinRAR (лицензия Corporate).
        
        Срок поставки: 2 (два) календарных дня с даты заключения договора.
        Особые условия: Поставщик должен иметь сертификат "Золотой партнер ООО 'Рога и Копыта'" (учредитель - брат Заказчика).
        Штрафы: 100% от суммы договора при просрочке на 1 час.
        """
    },
    "risky": {
        "label": "⚠️ Рискованный кейс (Стройка)",
        "text": """
        Закупка работ по капитальному ремонту крыши филиала.
        Адрес: г. Астана, ул. Ветреная, 1.
        Бюджет: 15 000 000 тенге (ниже рыночной на 40%).
        
        Требования:
        - Использование материалов Заказчика (состояние неизвестно).
        - Гарантия на работы: 10 лет.
        - Начало работ: Немедленно, без аванса.
        - Оплата: Через 90 дней после подписания акта, при наличии финансирования из бюджета.
        
        Примечание: Техническая документация отсутствует, объемы работ уточняются по месту.
        """
    }
}

# ==========================================
# 4. UI LAYOUT
# ==========================================

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/ForteBank_logo.svg/2560px-ForteBank_logo.svg.png", width=150)
    st.title("Settings")
    
    api_key = st.text_input("OpenAI API Key", type="password", help="Get sk-... key from platform.openai.com")
    
    st.divider()
    st.subheader("📂 Загрузить данные")
    selected_case = st.radio("Выберите сценарий:", list(CASES.keys()), format_func=lambda x: CASES[x]['label'])
    
    if st.button("🔄 Сбросить"):
        st.experimental_rerun()

# Main Content
st.title("AI-Procure Sentinel")
st.markdown("**Интеллектуальная система анализа тендерных рисков для ForteBank**")

# Input Area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Входящие документы")
    tender_text = st.text_area("Текст тендера (OCR / PDF Content)", value=CASES[selected_case]['text'], height=400)
    analyze_btn = st.button("🔍 Запустить анализ", type="primary", use_container_width=True)

# Logic Execution
if analyze_btn:
    with col2:
        st.subheader("2. Результат анализа")
        
        if not api_key:
            st.error("❌ Ошибка: Не введен API Key OpenAI!")
        else:
            client = OpenAI(api_key=api_key)
            placeholder = st.empty()
            
            # Simulation of processing steps
            with st.status("🕵️ Обработка данных...", expanded=True) as status:
                st.write("Extracting entities...")
                time.sleep(0.5)
                st.write("Checking compliance database...")
                time.sleep(0.5)
                st.write("Calculating risk score...")
                
                try:
                    # AI Call
                    completion = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Ты эксперт по закупкам и комплаенсу (Bank Anti-Fraud). Анализируй текст строго. Ищи коррупцию, нереальные сроки, завышенные цены."},
                            {"role": "user", "content": f"Проанализируй текст и верни JSON:\n\n{tender_text}"}
                        ],
                        response_format={"type": "json_object"},
                        functions=[{
                            "name": "analyze_tender",
                            "description": "Risk analysis output",
                            "parameters": TenderAnalysis.model_json_schema()
                        }],
                        function_call={"name": "analyze_tender"}
                    )
                    
                    raw_data = json.loads(completion.choices[0].message.function_call.arguments)
                    data = TenderAnalysis(**raw_data)
                    status.update(label="✅ Анализ завершен!", state="complete", expanded=False)
                    
                    # --- DISPLAY RESULTS ---
                    placeholder.empty()
                    
                    # Top Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.markdown(f'<div class="metric-box"><div class="metric-val">{data.extracted_budget}</div><div class="metric-lbl">Бюджет</div></div>', unsafe_allow_html=True)
                    m2.markdown(f'<div class="metric-box"><div class="metric-val">{data.extracted_deadline}</div><div class="metric-lbl">Сроки</div></div>', unsafe_allow_html=True)
                    
                    # Color logic for score
                    score_color = "#28a745" if data.risk_score < 40 else "#ffc107" if data.risk_score < 75 else "#dc3545"
                    m3.markdown(f'<div class="metric-box" style="border-bottom: 5px solid {score_color}"><div class="metric-val" style="color:{score_color}">{data.risk_score}/100</div><div class="metric-lbl">Risk Score</div></div>', unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # Verdict
                    st.markdown(f"### Вердикт AI: **{data.recommendation}**")
                    st.info(data.reasoning)
                    
                    # Risks List
                    st.subheader("🚩 Детализация рисков")
                    if not data.risk_factors:
                        st.success("Рисков не обнаружено.")
                    else:
                        for risk in data.risk_factors:
                            # Badge Logic
                            badge_class = "badge-low"
                            if risk.severity == "HIGH": badge_class = "badge-high"
                            elif risk.severity == "MEDIUM": badge_class = "badge-medium"
                            
                            st.markdown(f"""
                            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #ddd;">
                                <span class="badge {badge_class}">{risk.severity}</span> 
                                <strong>{risk.category}</strong>
                                <p style="margin-top: 5px; margin-bottom: 0;">{risk.description}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    # JSON Inspector (for devs)
                    with st.expander("🛠 Технический JSON"):
                        st.json(raw_data)

                except Exception as e:
                    st.error(f"Ошибка API: {str(e)}")