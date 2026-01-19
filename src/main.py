import os
from dotenv import load_dotenv
# استيراد الوكلاء اللي صاوبنا
from src.agents.triage_agent import TriageAgent
from src.agents.rag_agent import RAGAgent

load_dotenv()

class ComplaintsSystem:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.rag_agent = RAGAgent()

    def process_new_complaint(self, text):
        print("\n" + "="*50)
        print("🚀 بدأت عملية معالجة الشكاية...")
        
        # 1. تحليل الشكاية وفهمها
        analysis = self.triage_agent.analyze_complaint(text)
        print(f"📍 التصنيف المكتشف: {analysis['category']}")
        print(f"⚠️ درجة الاستعجال: {analysis['urgency']}")

        # 2. استشارة القانون (RAG)
        print("🔍 جاري البحث في القاعدة القانونية المغربية...")
        legal_report = self.rag_agent.get_legal_advice(
            analysis['category'], 
            analysis['summary_ar']
        )

        # 3. تجميع النتيجة النهائية
        final_report = {
            "metadata": analysis,
            "legal_basis": legal_report
        }
        
        return final_report

if __name__ == "__main__":
    system = ComplaintsSystem()
    
    # مثال لشكاية بالدارجة
    my_complaint = "البارح طاح واحد البوطو ديال الضو فالحومة وقريب يوقع مشكل، عافاكم ديرو شي حل"
    
    report = system.process_new_complaint(my_complaint)
    
    print("\n📝 التقرير النهائي:")
    print(f"الموضوع: {report['metadata']['summary_ar']}")
    print(f"الرأي القانوني:\n{report['legal_basis']}")
    print("="*50 + "\n")