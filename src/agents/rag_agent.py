import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.tools.retriever import get_retriever

# تحميل المتغيرات من .env
load_dotenv()

# Hardcoded base URL - no environment variable needed
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def clean_env_var(value):
    """Remove all non-printable characters from a string."""
    if not value:
        return ""
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value).strip()

class RAGAgent:
    def __init__(self):
        # إعداد الموديل عبر OpenRouter
        self.llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            openai_api_key=clean_env_var(os.getenv("OPENROUTER_API_KEY")),
            openai_api_base=OPENROUTER_BASE_URL
        )
        # جلب أداة البحث من الملف اللي صاوبنا
        self.retriever = get_retriever()

    def get_legal_advice(self, category, summary):
        # 1. البحث عن النصوص القانونية المرتبطة بالشكاية
        query = f"اختصاصات الجماعة في قطاع {category} و {summary}"
        docs = self.retriever.invoke(query)
        
        # تجميع النصوص المستخرجة
        context = "\n\n".join([d.page_content for d in docs])

        # 2. إعداد الـ System Prompt
        system_prompt = """
        أنت مستشار قانوني خبير في القانون التنظيمي للجماعات بالمغرب (113.14).
        بناءً على النصوص القانونية المقدمة، حدد بوضوح:
        1. المادة القانونية التي تنظم هذا المجال.
        2. هل هذا الاختصاص ذاتي للجماعة أم مشترك.
        3. مقترح للإجراء الذي يجب على البلدية اتخاذه.
        
        استعمل لغة مهنية واضحة ومباشرة.
        """

        # 3. بناء الـ Prompt باستخدام المتغيرات لتجنب أخطاء الـ Formatting
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "السياق القانوني المستخرج:\n{context_text}\n\nنص الشكاية:\n{summary_text}")
        ])

        # 4. إنشاء السلسلة (Chain) وتنفيذها
        chain = prompt | self.llm
        
        # تمرير البيانات كـ Dictionary لضمان التعامل السليم مع الرموز
        response = chain.invoke({
            "context_text": context,
            "summary_text": summary
        })

        return response.content

# كود تجريبي للتأكد من عمل الوكيل بشكل منفصل
if __name__ == "__main__":
    rag = RAGAgent()
    print("--- تجربة وكيل البحث القانوني ---")
    advice = rag.get_legal_advice("إنارة", "البولة طافية فالحومة هادي سيمانة")
    print(advice)