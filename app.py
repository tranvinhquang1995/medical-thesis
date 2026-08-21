import os
import streamlit as st
from translator_text import translate_medical_text
from translator_file import translate_docx, translate_pdf
from lit_search import perform_literature_search
from deep_search import optimize_search_prompt, deep_search_with_gemini, deep_search_with_academic_db

# Set page configuration
st.set_page_config(
    page_title="Medical Thesis - Trợ Lý Nghiên Cứu Y Khoa",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Medical Theme (Teal and Blue)
st.markdown("""
<style>
    .main {
        background-color: #f7fafc;
    }
    .stApp {
        background-color: #f7fafc;
    }
    h1 {
        color: #0f4c5c;
        font-family: 'Segoe UI', sans-serif;
    }
    h2 {
        color: #e36414;
    }
    .stButton>button {
        background-color: #0f4c5c;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #fb8b24;
        color: white;
    }
    .api-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
        border: 1px solid #ffeeba;
    }
</style>
""", unsafe_allow_html=True)

# Main Title and Description
st.title("🏥 Medical Thesis - Trợ Lý Nghiên Cứu Y Khoa")
st.markdown("---")

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/illustrations/external-doctor-working-from-home-flat-flat-medical-illustration/256/external-doctor-working-from-home-flat-flat-medical-illustration.png", width=150)
st.sidebar.title("Cấu hình hệ thống")

# --- STREAMLIT SECRETS INTEGRATION ---
# Attempt to read keys from Streamlit Secrets automatically
secrets_gemini = ""
secrets_s2 = ""

try:
    if "GEMINI_API_KEY" in st.secrets:
        secrets_gemini = st.secrets["GEMINI_API_KEY"]
    elif "gemini_api_key" in st.secrets:
        secrets_gemini = st.secrets["gemini_api_key"]
except Exception:
    pass

try:
    if "SEMANTIC_SCHOLAR_API_KEY" in st.secrets:
        secrets_s2 = st.secrets["SEMANTIC_SCHOLAR_API_KEY"]
    elif "semantic_scholar_api_key" in st.secrets:
        secrets_s2 = st.secrets["semantic_scholar_api_key"]
except Exception:
    pass

# API Keys Ingestion UI (Auto-filled if present in Secrets)
gemini_api_key = st.sidebar.text_input(
    "Hệ thống AI Key (Bắt buộc)",
    value=secrets_gemini,
    type="password",
    help="Lấy API key tại trang cung cấp khóa dịch vụ AI Studio. Tự động lấy từ Secrets nếu đã được cấu hình."
)

s2_api_key = st.sidebar.text_input(
    "Cơ sở dữ liệu học thuật Key (Tùy chọn)",
    value=secrets_s2,
    type="password",
    help="Không bắt buộc do cơ sở dữ liệu học thuật quốc tế được dùng miễn phí. Điền vào nếu bạn muốn nâng tốc độ/hạn mức truy cập."
)

# Select Model UI Mapping to hide underlying models
model_display = {
    "AI Engine - Flash (Khuyên dùng)": "gemini-2.5-flash",
    "AI Engine - Pro (Chuyên sâu)": "gemini-2.5-pro",
    "AI Engine - Lite (Tốc độ)": "gemini-1.5-flash"
}

selected_model_ui = st.sidebar.selectbox(
    "Chọn phiên bản Trí tuệ nhân tạo (AI Version)",
    list(model_display.keys()),
    index=0,
    help="Mặc định là phiên bản Flash - có hiệu năng cực kỳ tốt, tốc độ phản hồi nhanh."
)
model_choice = model_display[selected_model_ui]

# Features Navigation
feature_tab = st.sidebar.radio(
    "Chọn tính năng sử dụng:",
    [
        "📝 Dịch thuật văn bản y khoa",
        "📂 Dịch file Docx, PDF",
        "🔍 Tìm kiếm tài liệu khoa học",
        "💡 Tìm kiếm tài liệu chuyên sâu"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Medical Thesis** là ứng dụng hỗ trợ đắc lực cho sinh viên, bác sĩ, và nhà nghiên cứu y học trong việc dịch thuật tài liệu y văn và tổng hợp nghiên cứu khoa học chính xác.
""")

# Copyright notice added
st.sidebar.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.85rem; font-weight: 500; margin-top: 20px;'>"
    "Developed by Nobita"
    "</div>", 
    unsafe_allow_html=True
)

# Check API Key
if not gemini_api_key:
    st.markdown("""
    <div class="api-warning">
        ⚠️ <strong>Yêu cầu cấu hình:</strong> Vui lòng nhập <strong>Hệ thống AI Key</strong> ở thanh bên trái hoặc cấu hình trong <strong>Streamlit Secrets</strong> để bắt đầu sử dụng tất cả các tính năng của ứng dụng.
    </div>
    """, unsafe_allow_html=True)
    st.info("Nếu chưa có API Key, bạn có thể đăng ký miễn phí tại [AI Studio](https://aistudio.google.com/).")

# ----------------- FEATURE 1: TEXT TRANSLATION -----------------
if feature_tab == "📝 Dịch thuật văn bản y khoa":
    st.header("📝 Dịch thuật văn bản y khoa chuyên ngành")
    st.write("Sử dụng AI dịch thuật tối ưu hóa cho lĩnh vực y tế, giữ nguyên thuật ngữ viết tắt, biệt dược và tên thuốc.")
    
    col1, col2 = st.columns(2)
    with col1:
        direction = st.selectbox("Chọn chiều dịch:", ["EN -> VI", "VI -> EN"], index=0)
    with col2:
        st.write("")  # Empty spacing
        
    src_text = st.text_area("Nhập văn bản cần dịch:", height=250, placeholder="Nhập câu hoặc đoạn văn y khoa vào đây...")
    
    if st.button("Bắt đầu dịch"):
        if not gemini_api_key:
            st.error("Vui lòng cấu hình Hệ thống AI Key trước!")
        elif not src_text.strip():
            st.warning("Vui lòng nhập văn bản cần dịch.")
        else:
            with st.spinner("Đang tiến hành dịch thuật chuẩn y văn..."):
                translated = translate_medical_text(src_text, direction, gemini_api_key, model_choice)
                
                st.markdown("### Kết quả dịch thuật:")
                st.write(translated)
                st.success("Dịch hoàn tất!")
                st.download_button(
                    label="Tải kết quả về dạng file Text (.txt)",
                    data=translated,
                    file_name="medical_translation.txt",
                    mime="text/plain"
                )

# ----------------- FEATURE 2: FILE TRANSLATION -----------------
elif feature_tab == "📂 Dịch file Docx, PDF":
    st.header("📂 Dịch thuật tài liệu y khoa (DOCX, PDF)")
    st.write("Dịch thuật toàn bộ file tài liệu y văn, giữ nguyên cấu trúc định dạng cơ bản và đảm bảo tính thống nhất ngữ cảnh thông qua *Stateful Chat Session*.")
    
    direction = st.selectbox("Chọn chiều dịch file:", ["EN -> VI", "VI -> EN"], index=0)
    
    uploaded_file = st.file_uploader("Tải lên file tài liệu (chấp nhận .docx, .pdf):", type=["docx", "pdf"])
    
    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
        st.write(f"📁 Đang chọn file: **{uploaded_file.name}**")
        
        if st.button("Dịch file tài liệu"):
            if not gemini_api_key:
                st.error("Vui lòng cấu hình Hệ thống AI Key trước!")
                st.stop()
                
            # Create scratch directories
            os.makedirs("/workspace/scratch/downloads", exist_ok=True)
            
            # Save uploaded file to temp path
            temp_input_path = os.path.join("/workspace/scratch/downloads", uploaded_file.name)
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            progress_bar = st.progress(0, text="Đang chuẩn bị file...")
            
            # File translation process
            try:
                if uploaded_file.name.endswith(".docx"):
                    output_filename = f"translated_{uploaded_file.name}"
                    temp_output_path = os.path.join("/workspace/scratch/downloads", output_filename)
                    
                    with st.spinner("Đang dịch file Word tuần tự..."):
                        translate_docx(temp_input_path, temp_output_path, direction, gemini_api_key, model_choice, progress_bar)
                    
                elif uploaded_file.name.endswith(".pdf"):
                    # Translate PDF to translated Word file (highly recommended)
                    output_filename = f"translated_{uploaded_file.name.replace('.pdf', '.docx')}"
                    temp_output_path = os.path.join("/workspace/scratch/downloads", output_filename)
                    
                    with st.spinner("Đang chuyển đổi và dịch trang PDF tuần tự..."):
                        translate_pdf(temp_input_path, temp_output_path, direction, gemini_api_key, model_choice, progress_bar)
                
                # Check file size to verify output
                if os.path.exists(temp_output_path) and os.path.getsize(temp_output_path) > 0:
                    progress_bar.progress(1.0, text="Dịch hoàn tất!")
                    st.success("Tài liệu của bạn đã dịch thành công!")
                    
                    with open(temp_output_path, "rb") as file:
                        btn = st.download_button(
                            label="📥 Tải xuống bản dịch (.docx)",
                            data=file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error("Xử lý file thất bại hoặc file đầu ra trống.")
                    
            except Exception as e:
                st.error(f"Đã xảy ra lỗi trong quá trình xử lý file: {str(e)}")

# ----------------- FEATURE 3: LITERATURE SEARCH -----------------
elif feature_tab == "🔍 Tìm kiếm tài liệu khoa học":
    st.header("🔍 Tìm kiếm tài liệu khoa học và y văn")
    st.write("Nhập từ khóa hoặc câu hỏi y học để hệ thống thực hiện tìm kiếm học thuật trực tuyến. Kết quả trả ra cam kết kèm theo nguồn gốc rõ ràng.")
    
    search_query = st.text_input("Nhập chủ đề hoặc từ khóa y văn cần tìm kiếm:", placeholder="Ví dụ: Thử nghiệm lâm sàng của thuốc Pembrolizumab trong điều trị ung thư phổi tế bào nhỏ...")
    
    if st.button("Tìm kiếm tài liệu"):
        if not gemini_api_key:
            st.error("Vui lòng cấu hình Hệ thống AI Key trước!")
        elif not search_query.strip():
            st.warning("Vui lòng nhập từ khóa tìm kiếm.")
        else:
            with st.spinner("Hệ thống đang rà soát dữ liệu y học toàn cầu và tổng hợp báo cáo..."):
                results = perform_literature_search(search_query, gemini_api_key, model_choice)
                
                st.markdown("### 📊 Báo cáo tổng hợp tài liệu học thuật:")
                st.markdown(results["report"])
                
                # Show sources explicitly
                if results["sources"]:
                    st.markdown("---")
                    st.markdown("### 🔗 Các nguồn tài liệu uy tín tìm thấy:")
                    # Deduplicate sources
                    seen = set()
                    unique_sources = []
                    for s in results["sources"]:
                        if s["url"] not in seen:
                            seen.add(s["url"])
                            unique_sources.append(s)
                            
                    for idx, src in enumerate(unique_sources):
                        st.markdown(f"**[{idx+1}]** [{src['title']}]({src['url']})")
                else:
                    st.info("Không phát hiện thêm nguồn cụ thể từ siêu dữ liệu.")

# ----------------- FEATURE 4: DEEP SEARCH (ACADEMIC DATABASE) -----------------
elif feature_tab == "💡 Tìm kiếm tài liệu chuyên sâu":
    st.header("💡 Tìm kiếm y học chuyên sâu qua Cơ sở dữ liệu học thuật")
    st.write("Hệ thống AI sẽ tối ưu hóa từ khóa của bạn thành chuỗi tiếng Anh chuyên sâu, sau đó trực tiếp truy vấn cơ sở dữ liệu học thuật khổng lồ và lập báo cáo nghiên cứu tổng quan khoa học.")
    
    deep_query = st.text_area("Nhập yêu cầu nghiên cứu/câu hỏi khóa luận y văn của bạn:", height=100, placeholder="Ví dụ: Cơ chế tác dụng của vắc xin mRNA thế hệ mới trong việc phòng ngừa biến chủng SARS-CoV-2...")
    
    if st.button("Bắt đầu tìm kiếm chuyên sâu"):
        if not gemini_api_key:
            st.error("Vui lòng cấu hình Hệ thống AI Key trước!")
        elif not deep_query.strip():
            st.warning("Vui lòng điền nội dung nghiên cứu.")
        else:
            # Step 1: Optimize prompt using AI Engine
            with st.status("Đang phân tích và tối ưu hóa từ khóa chuyên ngành...", expanded=True) as status:
                st.write("🤖 Đang dịch thuật và biên soạn sang thuật ngữ MeSH tiếng Anh...")
                optimized_eng_query = optimize_search_prompt(deep_query, gemini_api_key, model_choice)
                st.write(f"🔑 **Từ khóa tiếng Anh chuyên sâu đã được tối ưu:** `{optimized_eng_query}`")
                
                st.write("🌍 Đang bắt đầu truy vấn chuyên sâu cơ sở dữ liệu học thuật...")
                
                # Call search with academic db
                results = deep_search_with_academic_db(
                    optimized_query=optimized_eng_query, 
                    api_key=gemini_api_key, 
                    model_name=model_choice,
                    db_api_key=s2_api_key if s2_api_key else None
                )
                
                status.update(label="Truy xuất hoàn tất!", state="complete", expanded=False)
                
            if results.get("success", False):
                st.markdown(f"### 🛡️ Báo cáo Tổng quan tài liệu y văn từ **{results['engine']}**:")
                st.markdown(results["report"])
                
                # Show sources explicitly
                if results["sources"]:
                    st.markdown("---")
                    st.markdown("### 📚 Danh mục bài báo khoa học chính xác:")
                    seen = set()
                    unique_sources = []
                    for s in results["sources"]:
                        if s["url"] not in seen and s["url"]:
                            seen.add(s["url"])
                            unique_sources.append(s)
                            
                    for idx, src in enumerate(unique_sources):
                        st.markdown(f"**[{idx+1}]** [{src['title']}]({src['url']})")
            else:
                st.error(f"Đã xảy ra lỗi: {results.get('error', 'Không xác định')}")
