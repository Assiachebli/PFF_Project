import os
import re
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# Hardcoded base URL - no environment variable needed
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def clean_env_var(value):
    """Remove all non-printable characters from a string."""
    if not value:
        return ""
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value).strip()

def get_retriever():
    persist_directory = "data/processed/chroma_db"
    
    # نفس الإعدادات اللي درنا ف الـ Ingestion
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        openai_api_key=clean_env_var(os.getenv("OPENROUTER_API_KEY")),
        openai_api_base=OPENROUTER_BASE_URL
    )
    
    # تحميل قاعدة البيانات
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    # تحويلها لـ Retriever (كيجيب أحسن 3 قطع مناسبة لكل سؤال)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

# تجربة صغيرة للتأكد
if __name__ == "__main__":
    retriever = get_retriever()
    results = retriever.invoke("ما هي اختصاصات الجماعة في مجال النظافة؟")
    print(f"تم العثور على {len(results)} نتائج من القانون.")
    for doc in results:
        print(f"- {doc.page_content[:100]}...")