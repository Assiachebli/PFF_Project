import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# تحميل المتغيرات من .env
load_dotenv()

def ingest_docs():
    # تأكدي أن الملف كاين ف هاد المسار
    pdf_path = "data/raw/loi_113_14.pdf"
    persist_directory = "data/processed/chroma_db"

    if not os.path.exists(pdf_path):
        print(f"❌ Error: الملف {pdf_path} غير موجود!")
        return

    print(f"--- جاري قراءة الملف: {pdf_path} ---")
    loader = PyPDFLoader(pdf_path)
    raw_documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    docs = text_splitter.split_documents(raw_documents)
    print(f"--- تم تقسيم النص إلى {len(docs)} قطعة ---")

    # التعديل المهم لـ OpenRouter
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small", # زيدي 'openai/' قبل اسم الموديل ف OpenRouter
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip('/') # كنحيدو الـ slash الأخير لضمان الخدمة
    )
    
    print("--- جاري إنشاء الـ Vector DB... (انتظري قليلاً) ---")
    
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    # حفظ البيانات محلياً
    vectorstore.persist() 
    print(f"✅ تم بنجاح! قاعدة البيانات محفوظة في: {persist_directory}")

if __name__ == "__main__":
    ingest_docs()