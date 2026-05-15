import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="NEBOSH Çözüm Sistemi", page_icon="🎓", layout="wide")

# Custom CSS for premium aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-weight: 800;
        font-size: 2.5rem;
        color: #0f172a;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.025em;
    }
    
    .sub-title {
        font-weight: 400;
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 2.5rem;
        text-align: center;
    }
    
    .footer-text {
        text-align: center;
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 4rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
        font-weight: 500;
    }
    
    .stButton>button {
        background-color: #0f172a;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1e293b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transform: translateY(-1px);
        color: white;
    }
    
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    .stTextArea>div>div>textarea:focus {
        border-color: #0f172a;
        box-shadow: 0 0 0 1px #0f172a;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">NEBOSH Sınav Çözüm Sistemi</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sınav metnini ve soruları girerek tam kapsamlı, formata uygun çözüm raporu oluşturun.</div>', unsafe_allow_html=True)

with st.expander("⚙️ Sistem Ayarları", expanded=True):
    api_key = st.text_input("Sistem Erişim Anahtarı:", type="password", placeholder="Erişim anahtarınızı buraya girin...")

if api_key:
    genai.configure(api_key=api_key)

exam_content = st.text_area("Sınav Metni (Senaryo ve Sorular):", height=350, placeholder="Tüm sınav içeriğini buraya yapıştırın...")

# Butonu ortalamak için kolonlar kullanıyoruz
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("Tüm Sınavı Çözümle", use_container_width=True)

st.write("")

if generate_button:
    if not api_key:
        st.warning("Lütfen sistem ayarlarından erişim anahtarınızı girin.")
    elif not exam_content:
        st.warning("Lütfen sınav içeriğini ilgili alana yapıştırın.")
    else:
        with st.spinner("Sınav analiz ediliyor ve çözümler hazırlanıyor. Lütfen bekleyin..."):
            try:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
                        available_models.append(m.name)
                
                if not available_models:
                    st.error("Geçerli bir erişim anahtarı bulunamadı veya yetkisiz erişim.")
                    st.stop()
                    
                model_name = next((name for name in available_models if 'pro' in name.lower()), available_models[0])
                model_name = model_name.replace("models/", "")
                
                model = genai.GenerativeModel(model_name)
                
                prompt = f"""Sen uzman bir NEBOSH İSG eğitmeni ve sınav değerlendiricisisin. 
Aşağıda sana bir NEBOSH Açık Kitap Sınavının (OBE) TAMAMI (Senaryo metni ve altındaki tüm görevler/sorular) verilmiştir.
Amacın, tüm görevleri (soruları) sırasıyla, NEBOSH değerlendirme standartlarına tam uyumlu ve sınavı geçecek kalitede cevaplamaktır.

KURALLAR:
1. KESİNLİKLE 'Merhaba', 'İşte cevaplar', 'Başarılar' gibi hiçbir selamlama, giriş veya kapanış metni YAZMA. Sadece "Görev 1" vb. başlık atıp doğrudan yanıta başla.
2. Metindeki tüm soruları sırasıyla cevapla. Her görev için ayrı bir başlık kullan.
3. Soruların yanındaki parantez içindeki puanları dikkate al. Puanlar kaç geçerli teknik nokta/argüman sunman gerektiğini gösterir. Her 1 puan için 1 geçerli madde yaz (Örn: 10 puanlık soruya en az 10 maddelik net açıklamalar).
4. ÇOK ÖNEMLİ: Eğer soruda "senaryodaki ilgili bilgileri kullanarak" veya "senaryoya dayalı" diyorsa, senaryodaki olayları, kişileri ve mekanları cevabına yansıt. Teorik bilgiyi mutlaka vaka ile birleştir.
5. KELİME SINIRI HEDEFİ: NEBOSH sınavlarında 3000 kelime sınırı vardır. Öğrencinin bunu aşmaması için senin toplamda tüm soruları yaklaşık 2500 kelime civarında çözmen gerekiyor. Bu yüzden yüksek puanlı soruları doyurucu bir şekilde (NEBOSH denetmenini ikna edecek şekilde uzun) açıkla. Cevapların sığ veya tek kelimelik olmasın.
6. Dili profesyonel Türkçe olsun.

SINAV METNİ (Senaryo ve Sorular):
{exam_content}

TÜM CEVAPLAR (Görev 1'den başlayarak):"""

                response = model.generate_content(prompt)
                
                st.success("Çözüm Raporu Başarıyla Oluşturuldu.")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")

st.markdown('<div class="footer-text">Not: Bu uygulama İş Güvenliği Uzmanı Fatih AKDENİZ tarafından geliştirilmiştir.</div>', unsafe_allow_html=True)
