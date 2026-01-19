import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

class TriageAgent:
    def __init__(self):
        # إعداد الموديل عبر OpenRouter
        # كنصحك بـ "anthropic/claude-3.5-sonnet" أو "openai/gpt-4o-mini" حيت واعرين ف الدارجة
        self.llm = ChatOpenAI(
            model="openai/gpt-4o-mini", 
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip('/')
        )

    def analyze_complaint(self, complaint_text):
        system_prompt = """
        أنت وكيل ذكي متخصص في تصنيف شكايات المواطنين في المغرب.
        مهمتك هي قراءة الشكاية (التي قد تكون بالدارجة المغربية) وتحويلها إلى بيانات منظمة.
        
        يجب أن يكون الرد بصيغة JSON فقط ويتضمن:
        - category: (ماء، إنارة، نفايات، طرق، إداري، أخرى)
        - urgency: (High, Medium, Low)
        - summary_ar: ملخص للشكاية بالعربية الفصحى
        - original_language: لغة الشكاية الأصلية
        
        سياق الدارجة:
        - "قادوس، مجاري، واد حار" -> تطهير سائل/ماء
        - "البولة، الظلام، الضو" -> إنارة عمومية
        - "الزبل، حاشاك، الطوبيس د النظافة" -> نفايات
        - "الحفرة، لكيود، الطريق" -> طرق
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "الشكاية: {complaint}")
        ])

        # ربط المكونات
        chain = prompt | self.llm | JsonOutputParser()
        
        return chain.invoke({"complaint": complaint_text})

# تجربة صغيرة
if __name__ == "__main__":
    agent = TriageAgent()
    test_complaint = "السلام عليكم، كاين واحد الحفرة كبيرة وسط الطريق فحي السلام، هرست لينا الرويضة ديال الطوموبيل"
    result = agent.analyze_complaint(test_complaint)
    print(result)