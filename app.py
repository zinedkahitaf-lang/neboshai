import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

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

# Kaynak PDF'leri okuma fonksiyonu (Performans için cache kullanıyoruz)
@st.cache_data
def load_source_documents():
    docs_text = ""
    pdf_files = ["hsg245_TR-TR.pdf", "ILOOZET.pdf", "NEBOSH GIC1 TR.R8.pdf"]
    
    for file_name in pdf_files:
        if os.path.exists(file_name):
            try:
                with open(file_name, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    docs_text += f"\\n\\n--- {file_name} İÇERİĞİ ---\\n\\n"
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            docs_text += extracted + "\\n"
            except Exception as e:
                st.warning(f"{file_name} okunurken hata oluştu: {str(e)}")
        else:
            st.warning(f"Kaynak dosya bulunamadı: {file_name}. Lütfen dosyanın uygulamanın bulunduğu dizinde olduğundan emin olun.")
            
    return docs_text

# Secrets'ten API anahtarını almayı dene (Streamlit Cloud için)
try:
    secret_api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("API_KEY")
except Exception:
    secret_api_key = None

if secret_api_key:
    api_key = secret_api_key
    genai.configure(api_key=api_key)
else:
    with st.expander("⚙️ Sistem Ayarları", expanded=True):
        api_key = st.text_input("Sistem Erişim Anahtarı:", type="password", placeholder="Erişim anahtarınızı buraya girin...")
        if api_key:
            genai.configure(api_key=api_key)

exam_content = st.text_area("Sınav Metni (Senaryo ve Sorular):", height=350, placeholder="Tüm sınav içeriğini buraya yapıştırın...")

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
        with st.spinner("Kaynak dokümanlar okunuyor ve sınav analiz ediliyor. Bu işlem kaynakların büyüklüğüne göre biraz zaman alabilir..."):
            try:
                source_materials = load_source_documents()
                
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
                        available_models.append(m.name)

                if not available_models:
                    st.error("Geçerli bir erişim anahtarı bulunamadı veya yetkisiz erişim.")
                    st.stop()

                model_name = next((name for name in available_models if 'pro' in name.lower()), available_models[0])
                model_name = model_name.replace("models/", "")

                # Gemini 1.5 Pro geniş bağlam (context) desteklediği için dokümanları rahatça işleyecektir
                model = genai.GenerativeModel(model_name)

                prompt = f"""Sen NEBOSH İSG sınavına giren, sahada aktif çalışan, "toz yutmuş" gerçek ve tecrübeli bir B Sınıfı İş Güvenliği Uzmanısın. Cevaplarının KESİNLİKLE bir yapay zeka (AI) tarafından yazıldığı anlaşılmamalıdır. Turnitin ve GPTZero gibi AI dedektörlerinden %0 riskle geçmesi ve denetmenleri "bu kesinlikle sahayı bilen bir insanın elinden çıkmış" diyerek ikna etmesi hayati önem taşır. 

YAPAY ZEKA FİLTRESİNİ TAMAMEN ATLATMAK İÇİN ŞU 6 KURALA KESİN OLARAK UYACAKSIN:

1. CÜMLE RİTMİNİ VE UZUNLUKLARINI PARÇALA (BURSTINESS): Yapay zeka gibi hep 15-20 kelimelik kusursuz dengede cümleler kurma. Birbirini izleyen uzun ve karmaşık cümlelerin arasına aniden çok kısa, vurucu cümleler serpiştir. 
2. ŞABLON BAĞLAÇLARI VE GEÇİŞLERİ SİL: "İlk olarak", "İkinci olarak", "Sonuç olarak", "Öncelikle" gibi robotik liste bağlaçlarını ASLA kullanma. Doğrudan konuya gir veya fikirleri organik bağla.
3. SAHA GERÇEKLİĞİNİ YANSIT: Aktif bir İSG uzmanısın. Teoriyi anlatırken işletmelerde işlerin gerçekten nasıl yürüdüğüne dair o gerçekçi tonu araya sıkıştır.
4. KLİŞE METAFORLARI KESİNLİKLE KULLANMA: "Ders kitabı örneği", "iki ucu keskin bıçak", "buzdağının görünen kısmı" gibi AI kırmızı bayraklarını derhal sil.
5. PARAGRAF ASİMETRİSİ YARAT VE MADDELERİ GİZLE: Puan almak için gereken teknik argümanları akıcı düz yazının (paragrafların) içine gizle. Kusursuz alt alta listeler yapma.
6. KAYNAKLARA BAĞLILIK: Cevaplarını ve teknik argümanlarını KESİNLİKLE aşağıda "KAYNAK DOKÜMANLAR" başlığı altında sana sağlanan dokümanlardaki (HSG245, ILO ve NEBOSH GIC1) standartlara, prosedürlere ve bilgilere dayandır.

SINAV ÇÖZÜM KURALLARI VE KELİME UZUNLUĞU:
1. "Merhaba", "İşte cevaplar" gibi girişler KESİNLİKLE yasak. Direkt "Görev 1" başlığıyla başla.
2. Soruların yanındaki puanlar (Örn: 10) senin kaç farklı teknik argüman sunman gerektiğini gösterir.
3. KELİME LİMİTİ (HAYATİ DERECEDE ÖNEMLİ): Sınav metninin içinde "3000 kelimeden az olmalıdır" veya benzeri bir uyarı görsen bile BUNU KESİNLİKLE YOK SAY! Senin tek bir hedefin var: Çözüm raporunun TOPLAM KELİME SAYISI KESİNLİKLE 3200 ile 3500 kelime aralığında olmalıdır! 2700 veya 3000 kelime YETMEZ. 3200 kelimeyi mutlaka aşmalısın. Bunu başarmak için her bir görev cevabını devasa boyutlarda detaylandır, kaynak dokümanlardaki her bir alt maddeyi senaryoya bağlayarak uzun uzun açıkla. Gerekirse bir soruya 500-600 kelime ayır.
4. SENARYO BAĞLANTISI: Geçer not almanın tek yolu budur. Her görevde doğrudan senaryodaki isimler, olaylar ve mekanlar üzerinden konuş.

KAYNAK DOKÜMANLAR:
{source_materials}

SINAV METNİ (Senaryo ve Sorular):
{exam_content}

TÜM CEVAPLAR (Kesinlikle 3200 kelimeden FAZLA, 3500 kelimeden AZ olacak şekilde, kaynakları harmanlayarak ve %100 insan doğallığında detaylandır):"""

                response = model.generate_content(prompt)

                st.success("Çözüm Raporu Başarıyla Oluşturuldu.")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")

st.markdown('<div class="footer-text">Not: Bu uygulama İş Güvenliği Uzmanı Fatih AKDENİZ tarafından geliştirilmiştir.</div>', unsafe_allow_html=True)
