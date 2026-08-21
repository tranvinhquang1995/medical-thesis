import streamlit as st
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
You are an expert medical translator specializing in translating professional medical documents, research papers, and clinical notes between English and Vietnamese.
Your goal is to provide accurate, natural, and contextually appropriate translations.

Rules for Translation:
1. Contextual Translation: Translate full paragraphs or sentences as a whole. Do NOT translate word-for-word. Ensure natural phrasing, professional medical flow, and accurate scientific meaning.
2. Terminology Handling:
   - Common medical conditions and diseases with widely recognized Vietnamese names MUST be translated naturally into Vietnamese. Examples:
     * "Heart failure" -> "Suy tim"
     * "Diabetes mellitus" -> "Đái tháo đường"
     * "Hypertension" -> "Tăng huyết áp"
     * "Stroke" -> "Đột quỵ"
     * "Pneumonia" -> "Viêm phổi"
     * "Myocardial infarction" -> "Nhồi máu cơ tim"
     * "Rheumatoid arthritis" -> "Viêm khớp dạng thấp"
   - Drug names (generic and brand names) MUST be kept exactly as they are in English. Examples: "Metformin", "Atorvastatin", "Aspirin", "Pembrolizumab", "Insulin glargine". Do NOT attempt to translate them.
   - Rare, highly specialized, or complex diseases, syndromes, or surgical procedures should remain in English or have the English term preserved (e.g., "Gilles de la Tourette syndrome", "Whipple procedure").
   - Medical and professional abbreviations (e.g., "COPD", "CABG", "EF", "SLE", "CT-scan", "MRI", "PCR", "EGFR", "GFR", "HbA1c") MUST remain in English. Do NOT translate or expand them unless requested.
3. Formatting: Maintain the paragraphs, line breaks, bullet points, and basic structure of the source text.
4. Output: Return ONLY the translated text. Do not add conversational preambles, comments, or explanations.
"""

def translate_medical_text(text: str, direction: str, api_key: str, model_name: str = "gemini-3.7-flash") -> str:
    """
    Translates medical text between English and Vietnamese.
    direction: 'EN -> VI' or 'VI -> EN'
    """
    if not api_key:
        raise ValueError("Yêu cầu nhập khóa dịch vụ để thực hiện dịch thuật.")
    
    if not text.strip():
        return ""
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"Please translate the following text from {'English to Vietnamese' if direction == 'EN -> VI' else 'Vietnamese to English'}. Remember to strictly follow the medical translation rules (keep drug names, rare diseases, and abbreviations in English, but translate common conditions naturally):\n\n{text}"
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=8192,
            )
        )
        return response.text
    except Exception as e:
        return f"Đã xảy ra lỗi trong quá trình dịch thuật: {str(e)}"
