import sys
import os
import base64
from dotenv import load_dotenv

# --- 0. Load Environment Variables FIRST ---
load_dotenv()

# Global Sanitization: Explicitly strip newline characters from all critical env vars
# This fixes the "Invalid non-printable ASCII character" error in Railway/Docker
for key in ["OPENROUTER_API_KEY", "OPENROUTER_BASE_URL", "OPENAI_API_KEY", "OPENAI_API_BASE"]:
    if os.getenv(key):
        os.environ[key] = os.getenv(key).strip()

import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io

# --- 1. System Setup ---
sys.path.append(os.getcwd())

# Import Agents (After load_dotenv to ensure keys are available)
try:
    from src.agents.triage_agent import TriageAgent
    from src.agents.rag_agent import RAGAgent
    from src.agents.reporter import ReportingAgent
except ImportError as e:
    st.error(f"Erreur d'importation des agents : {e}")

# --- 2. Page Configuration ---
st.set_page_config(
    page_title="CitizenAI - Gestion Intelligente",
    page_icon="🇲🇦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 3. Custom CSS (Glassmorphism, Responsive, French LTR) ---
st.markdown("""
    <style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Deep Blue Theme (#0040ff) */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 50% 50%, rgba(0, 64, 255, 0.1) 0%, transparent 50%);
        background-attachment: fixed;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(14, 17, 23, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(0, 64, 255, 0.3); /* #0040ff border */
        padding: 30px;
        box-shadow: 0 0 20px rgba(0, 64, 255, 0.1);
        margin-bottom: 20px;
        width: 100%;
        transition: transform 0.2s;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        border-color: #0040ff;
        box-shadow: 0 0 30px rgba(0, 64, 255, 0.2);
    }

    /* Download Card Special Style */
    .download-card {
        background: rgba(0, 64, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid #0040ff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-top: 20px;
    }

    /* Custom HTML Button Style */
    a.custom-download-btn {
        display: inline-block;
        background-color: #0040ff;
        color: white !important;
        padding: 12px 30px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(0, 64, 255, 0.4);
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    a.custom-download-btn:hover {
        background-color: #1a53ff;
        transform: scale(1.03);
        box-shadow: 0 0 25px rgba(0, 64, 255, 0.6);
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #0040ff !important;
        box-shadow: 0 0 10px rgba(0, 64, 255, 0.3) !important;
    }
    label {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Buttons (#0040ff) */
    .stButton button {
        background: #0040ff !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 30px !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
        width: 100%;
        box-shadow: 0 0 15px rgba(0, 64, 255, 0.4) !important;
    }
    .stButton button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 25px rgba(0, 64, 255, 0.6) !important;
        background: #1a53ff !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: rgba(14, 17, 23, 0.8);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 64, 255, 0.2);
    }
    [data-testid="stMetricLabel"] { color: rgba(255, 255, 255, 0.7); }
    [data-testid="stMetricValue"] { color: #0040ff; font-size: 1.6rem; }

    /* Login Specifics */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 80vh;
    }
    .login-container {
        width: 100%;
        max-width: 450px;
        margin: auto;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .glass-card, .download-card { padding: 20px; margin-bottom: 15px; }
        h1 { font-size: 1.8rem !important; }
        h3 { font-size: 1.2rem !important; }
        [data-testid="stMetric"] { margin-bottom: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Helper Functions ---
def create_pdf(report_text):
    """Generates a PDF from the report text."""
    if not report_text:
        return None
        
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        
        # Title
        pdf.set_font("Helvetica", 'B', 16)
        # Fix: txt -> text, ln -> new_x/new_y for fpdf2 using Enums
        pdf.cell(200, 10, text="Rapport Decisionnel - CitizenAI", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.ln(10)
        
        # Body
        pdf.set_font("Helvetica", size=11)
        # Handle unicode roughly with latin-1 replacement
        safe_text = str(report_text).encode('latin-1', 'replace').decode('latin-1')
        # Fix: txt -> text
        pdf.multi_cell(0, 10, text=safe_text)
        
        # Correctly handling fpdf2 byte output
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erreur PDF: {e}")
        return None

# --- 5. State Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Ensure API Key and Base URL are loaded
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("⚠️ Erreur Critique : Clé API `OPENROUTER_API_KEY` manquante dans le fichier .env")
    st.stop()

# --- 6. Views ---

def login_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("""
            <div class='glass-card' style='text-align: center; border-top: 5px solid #0040ff;'>
                <h1 style='color: white; margin-bottom: 10px;'>CitizenAI</h1>
                <p style='color: rgba(255,255,255,0.6);'>Portail Intelligent de Gestion des Plaintes</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            st.text_input("Nom d'utilisateur", placeholder="admin")
            st.text_input("Mot de passe", type="password", placeholder="****")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Se connecter"):
                st.session_state['logged_in'] = True
                st.rerun()
        
        st.markdown("""
            <div style='text-align: center; margin-top: 20px;'>
                <span style='font-size: 1.5rem; color: rgba(255,255,255,0.5); margin: 0 10px;'></span>
                <span style='font-size: 1.5rem; color: rgba(255,255,255,0.5); margin: 0 10px;'></span>
                <span style='font-size: 1.5rem; color: rgba(255,255,255,0.5); margin: 0 10px;'></span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def dashboard_view():
    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 Admin Communal")
        if st.button("Déconnexion"):
            st.session_state['logged_in'] = False
            st.rerun()

    # Header
    st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: white; text-shadow: 0 0 20px rgba(0, 64, 255, 0.5);'>Tableau de Bord Citoyen</h1>
            <p style='color: rgba(255,255,255,0.6);'>Analyse IA selon la Loi 113.14</p>
        </div>
    """, unsafe_allow_html=True)

    # Input Area
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: white;'>📝 Nouvelle Plainte</h3>", unsafe_allow_html=True)
    user_input = st.text_area("Description du problème", height=120, placeholder="Ex: Panne d'éclairage public...", label_visibility="collapsed")
    process = st.button("🚀 Lancer l'Analyse")
    st.markdown("</div>", unsafe_allow_html=True)

    if process and user_input:
        with st.spinner("🔄 Analyse en cours par les agents IA..."):
            try:
                # 1. Triage Agent
                triage_agent = TriageAgent()
                analysis = triage_agent.analyze_complaint(user_input)
                
                if not analysis:
                     st.error("Erreur : L'agent de triage n'a renvoyé aucune réponse. Vérifiez la connexion API.")
                     return

                # 2. RAG Agent
                rag_agent = RAGAgent()
                legal_advice = rag_agent.get_legal_advice(analysis.get('category', 'Général'), analysis.get('summary_ar', ''))

                # 3. Reporting Agent
                reporting_agent = ReportingAgent()
                final_report = reporting_agent.generate_report(analysis, legal_advice)
                
                if not final_report:
                    st.error("Erreur : Impossible de générer le rapport final.")
                    return

                # --- Results Display ---
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Catégorie", analysis.get('category', 'N/A'))
                c2.metric("Urgence", analysis.get('urgency', 'N/A'))
                c3.metric("Langue Détectée", analysis.get('original_language', 'N/A'))
                st.markdown("<br>", unsafe_allow_html=True)

                # Cards (Summaries only)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div class='glass-card' style='border-left: 4px solid #0040ff;'>
                            <h4 style='color: white;'>📄 Résumé Administratif</h4>
                            <p style='color: #ccc; font-size: 0.9em;'>{analysis.get('summary_ar', 'N/A')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class='glass-card' style='border-left: 4px solid #0040ff;'>
                            <h4 style='color: white;'>⚖️ Avis Juridique</h4>
                            <div style='color: #ccc; font-size: 0.9em;'>{legal_advice if legal_advice else "Non disponible"}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # Final Success Message and Download (Unified)
                st.markdown("<br>", unsafe_allow_html=True)
                
                pdf_bytes = create_pdf(final_report)
                if pdf_bytes:
                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="rapport_decisionnel.pdf" class="custom-download-btn">📥 Télécharger le Rapport Officiel (PDF)</a>'
                    
                    st.markdown(f"""
                        <div class='download-card'>
                            <h3 style='color: white; margin-bottom: 10px;'>✅ Analyse complétée avec succès</h3>
                            <p style='color: rgba(255,255,255,0.7); margin-bottom: 20px;'>Votre rapport est prêt ci-dessous.</p>
                            {href}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Erreur lors de la génération du PDF.")

            except Exception as e:
                st.error(f"Une erreur système est survenue : {e}")

# --- 7. Main Loop ---
if st.session_state['logged_in']:
    dashboard_view()
else:
    login_view()