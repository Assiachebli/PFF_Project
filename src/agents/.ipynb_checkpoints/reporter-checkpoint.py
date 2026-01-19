import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ReportingAgent:
    def __init__(self):
        # تأكدي أن المفتاح كاين فـ .env
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) 
        self.parser = StrOutputParser()

    def generate_report(self, analysis, legal_advice):
        """
        Consolide les résultats des autres agents en un rapport décisionnel.
        """
        template = """
        Tu es un Expert en Administration Publique Marocaine (Loi 113.14).
        Ta mission est de rédiger un rapport de décision basé sur l'analyse technique et l'avis juridique fournis.

        --- DONNÉES D'ENTRÉE ---
        1. Analyse Technique (Triage): {analysis}
        2. Avis Juridique (RAG): {legal_advice}

        --- FORMAT DU RAPPORT (EN FRANÇAIS) ---
        Rédige le rapport sous la forme suivante (utilise Markdown) :

        ### 📋 RAPPORT DÉCISIONNEL
        **1. Résumé de la Situation :** (Une phrase claire)
        **2. Analyse de Gravité :** (Urgence + Impact sur le citoyen)
        **3. Base Légale Applicable :** (Citer les articles mentionnés dans l'avis juridique)
        **4. Action Immédiate Recommandée :** (Ce que le président de la commune doit ordonner)
        **5. Service Responsable :** (Identifier le service concerné : Travaux, Environnement, Urbanisme, etc.)
        """

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        
        report = chain.invoke({
            "analysis": analysis,
            "legal_advice": legal_advice
        })
        return report