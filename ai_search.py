import streamlit as st
import urllib.parse
from google import genai
from google.genai import types

def optimize_search_prompt_for_external(user_query: str, api_key: str, model_name: str = "gemini-3.7-flash") -> str:
    """
    Step 1: Analyzes the user's query and translates/expands it into an incredibly detailed,
    comprehensive English academic search prompt containing specialized scientific terms, MeSH terms,
    synonyms, and query structure designed to be fed into external research engines.
    """
    if not api_key:
        return user_query
        
    client = genai.Client(api_key=api_key)
    system_prompt = (
        "You are an elite clinical research advisor. Your task is to analyze the user's research topic "
        "(which could be in Vietnamese or English) and expand it into a highly sophisticated, "
        "comprehensive, and detailed English search prompt/paragraph designed for advanced AI search engines. "
        "Do not just output keywords. Instead, write a detailed scientific inquiry paragraph that specifies: "
        "1. The core pathology or clinical intervention (including key scientific terms and MeSH synonyms). "
        "2. The target population, clinical trial outcomes, and key metrics to find. "
        "3. A directive to search for peer-reviewed studies, clinical guidelines, and high-impact reports. "
        "Your output must be a single, cohesive, highly professional English paragraph (approx 50-80 words). "
        "Do not include introduction, explanations, quotes, or conversational preambles. Output ONLY the prompt."
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=f"Generate a sophisticated English search prompt for this medical topic: {user_query}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3
            )
        )
        return response.text.strip()
    except Exception:
        # Fallback to simple query expansion
        return f"Provide a detailed clinical review on {user_query}, focusing on clinical trials, guidelines, and efficacy."

def render_ai_search_tab(api_key: str, model_name: str = "gemini-3.7-flash"):
    st.header("🌐 Tìm kiếm từ nguồn AI & Cơ sở dữ liệu học thuật quốc tế")
    st.write(
        "Nhập từ khóa hoặc chủ đề nghiên cứu của bạn. Hệ thống AI sẽ tự động phân tích, dịch thuật và tối ưu hóa "
        "thành một **Siêu Prompt (Super Prompt) bằng tiếng Anh chuyên môn sâu**. Sau đó, bạn chỉ cần nhấp chuột vào các nút "
        "chuyển tiếp tương ứng để mở trang tìm kiếm của các công cụ hàng đầu thế giới hoàn toàn miễn phí và không cần đăng nhập!"
    )
    
    # Initialize session state for storing optimized query
    if "optimized_external_prompt" not in st.session_state:
        st.session_state.optimized_external_prompt = ""
    if "last_user_query_external" not in st.session_state:
        st.session_state.last_user_query_external = ""
        
    user_query = st.text_area(
        "Nhập chủ đề hoặc câu hỏi nghiên cứu của bạn (Tiếng Anh hoặc Tiếng Việt):",
        height=100,
        placeholder="Ví dụ: Đánh giá hiệu quả lâm sàng của liệu pháp tế bào gốc trong điều trị thoái hóa khớp gối..."
    )
    
    # Trigger analysis on button click or if query changes
    if st.button("Phân tích & Tạo Siêu Prompt Học Thuật"):
        if not user_query.strip():
            st.warning("Vui lòng nhập chủ đề cần tìm kiếm.")
        else:
            with st.spinner("Đang phân tích thuật ngữ y sinh và thiết lập Siêu Prompt học thuật..."):
                optimized_prompt = optimize_search_prompt_for_external(user_query, api_key, model_name)
                st.session_state.optimized_external_prompt = optimized_prompt
                st.session_state.last_user_query_external = user_query
                st.success("Tạo Siêu Prompt thành công!")
                
    # If we have an optimized prompt, display it and render redirect buttons
    if st.session_state.optimized_external_prompt:
        st.markdown("### 🔑 Siêu Prompt Học Thuật Tiếng Anh (Đã tối ưu hóa):")
        st.info(st.session_state.optimized_external_prompt)
        
        st.markdown("---")
        st.markdown("### 🚀 Chọn công cụ chuyển tiếp để tìm kiếm (Không cần đăng nhập):")
        st.write(
            "Nhấp vào bất kỳ công cụ nào dưới đây, trình duyệt sẽ tự động chuyển hướng và nhập sẵn "
            "Siêu Prompt học thuật của bạn vào ô tìm kiếm của công cụ đó. Bạn chỉ cần nhấn **Enter** để nhận kết quả!"
        )
        
        # URL encode the query for safe link redirection
        encoded_prompt = urllib.parse.quote(st.session_state.optimized_external_prompt)
        
        # Define URLs for free, no-login academic and AI tools
        semantic_scholar_url = f"https://www.semanticscholar.org/search?q={encoded_prompt}"
        consensus_url = f"https://consensus.app/results/?q={encoded_prompt}"
        perplexity_url = f"https://www.perplexity.ai/search?q={encoded_prompt}"
        pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={encoded_prompt}"
        brave_ai_url = f"https://search.brave.com/search?q={encoded_prompt}&source=all"
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📚 Các cơ sở dữ liệu y văn & bài báo khoa học:")
            st.link_button(
                "🔍 Semantic Scholar (Miễn phí - Đọc 200M+ bài báo khoa học)", 
                url=semantic_scholar_url,
                use_container_width=True
            )
            st.caption("Công cụ tìm kiếm AI từ Viện Allen, tối ưu hóa mức độ ảnh hưởng của trích dẫn và tóm tắt siêu ngắn.")
            
            st.write("") # Spacing
            
            st.link_button(
                "📊 Consensus (Miễn phí - Đánh giá tỷ lệ đồng thuận khoa học)", 
                url=consensus_url,
                use_container_width=True
            )
            st.caption("AI học thuật tốt nhất để thống kê tỷ lệ đồng thuận của các nghiên cứu lâm sàng về một câu hỏi.")
            
            st.write("") # Spacing
            
            st.link_button(
                "⚕️ PubMed (Miễn phí - Thư viện Y khoa Quốc gia Hoa Kỳ)", 
                url=pubmed_url,
                use_container_width=True
            )
            st.caption("Thư viện y khoa lớn nhất thế giới, chứa hàng chục triệu bản ghi, thử nghiệm lâm sàng vàng.")
            
        with col2:
            st.markdown("##### 🌍 Các công cụ AI tìm kiếm tổng hợp trực tiếp:")
            st.link_button(
                "⚡ Perplexity AI (Miễn phí - Trả lời tổng hợp & Chú thích nguồn)", 
                url=perplexity_url,
                use_container_width=True
            )
            st.caption("Công cụ tìm kiếm hội thoại thông minh, trả lời trực tiếp kèm link nguồn tham khảo thực tế thời gian thực.")
            
            st.write("") # Spacing
            
            st.link_button(
                "🦁 Brave Search AI (Miễn phí - Công cụ tìm kiếm bảo mật kèm AI)", 
                url=brave_ai_url,
                use_container_width=True
            )
            st.caption("Hệ thống tìm kiếm bảo mật tích hợp mô hình AI Leo tự động trả lời, tóm tắt và trích xuất nguồn từ trang web.")
            
        # Subtle tip footer
        st.markdown(
            "<div style='background-color: #e6f7ff; color: #0050b3; padding: 12px; border-radius: 8px; font-size: 0.9rem; margin-top: 20px; border-left: 5px solid #1890ff;'>"
            "💡 <strong>Mẹo nhỏ cho Nobita:</strong> Khi bấm chuyển tiếp sang các trang trên, nếu công cụ có hỏi "
            "đăng nhập, bạn hoàn toàn có thể bỏ qua (click Close / Skip) để tiếp tục xem và tải các bài nghiên cứu hoàn toàn miễn phí!"
            "</div>",
            unsafe_allow_html=True
        )
