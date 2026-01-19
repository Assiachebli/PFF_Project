import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def get_retriever():
    persist_directory = "data/processed/chroma_db"
    
    # نفس الإعدادات اللي درنا ف الـ Ingestion
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        openai_api_key=os.getenv("OPENROUTER_API_KEY", "").strip(),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip().rstrip('/')
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