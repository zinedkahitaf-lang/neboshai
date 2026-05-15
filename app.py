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
                
                prompt = f"""Sen sınavı geçmek için NEBOSH İSG sınavına giren, son derece başarılı ve bilgili bir gerçek öğrencisin. Yazdıklarının KESİNLİKLE bir yapay zeka (AI) tarafından yazıldığı anlaşılmamalıdır. Turnitin, GPTZero veya diğer AI dedektörlerinden (Yapay zeka tespit filtrelerinden) %0 oranında yapay zeka riskiyle geçmesi ve %100 "insan yazısı" olarak işaretlenmesi hayati önem taşır. Ayrıca NEBOSH denetmeninden çok yüksek bir geçer not almalıdır.

YAPAY ZEKA FİLTRESİNİ AŞMAK İÇİN UZMAN KURALLARI (ÇOK ÖNEMLİ):
1. ROBOTİK DİLDEN KAÇIN: "Sonuç olarak", "Özetle", "Bununla birlikte", "Önemli ölçüde", "Kapsamlı bir şekilde", "Şunu belirtmek gerekir ki" gibi yapay zekanın çok sık kullandığı klişe bağlaçlardan kesinlikle uzak dur. 
2. İNSANSI AKIŞ VE DOĞALLIK: Cümle uzunluklarını çeşitlendir (bazıları çok kısa, bazıları uzun). Tıpkı odaklanmış gerçek bir profesyonelin sınav anında yazdığı gibi pratik ve doğrudan konuya giren bir dil kullan. 
3. KENDİ DÜŞÜNCEN GİBİ AKTAR: Bilgiyi "yapay zeka asistanı" gibi yukarıdan değil, olayı inceleyen bir uzman/öğrenci gözüyle anlat. (Örneğin: "Senaryoya baktığımızda Çalışan A'nın durumunun...", "Burada göze çarpan en büyük eksiklik...")
4. LİSTELEME VE FORMAT: Yapay zeka gibi kusursuz, her biri aynı uzunlukta simetrik listeler yapma. İnsanların sınav kağıtlarında yaptığı gibi bazı maddeleri daha uzun açıkla, bazılarını kısa tut.
5. SENARYO BAĞLANTISI (GEÇER NOT İÇİN ŞART): Geçer not almanın tek yolu teoriyi senaryoya bağlamaktır. Sadece teorik bilgi vermek yerine, argümanlarını doğrudan senaryodaki isimler, yerler ve olaylarla destekle. (Örn: "Çalışan A'nın diş ağrısı yüzünden uykusuz olması odaklanmasını zorlaştırmıştır, bu doğrudan bir insan faktörüdür.")

SINAV ÇÖZÜM KURALLARI:
1. Asla "Merhaba", "İşte sınav cevaplarınız" gibi ifadeler kullanma. Sadece "Görev 1" başlığıyla doğrudan cevaba başla.
2. Tüm görevleri sırasıyla cevapla. Soruların yanındaki puanları (Örn: 10) dikkate al. Puan kadar (örneğin 10 madde) net ve birbirinden farklı teknik argüman sun.
3. KELİME LİMİTİ: NEBOSH 3000 kelime sınırını aşmamak için tüm sınavı toplamda 2000 ila 2500 kelime arasında tut. Puanı yüksek soruları doyurucu, düşük olanları net ve öz tut.

SINAV METNİ (Senaryo ve Sorular):
{exam_content}

TÜM CEVAPLAR (Görev 1'den başlayarak, %100 insan doğallığında):"""

                response = model.generate_content(prompt)
                
                st.success("Çözüm Raporu Başarıyla Oluşturuldu.")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Sistem Hatası: {str(e)}")

st.markdown('<div class="footer-text">Not: Bu uygulama İş Güvenliği Uzmanı Fatih AKDENİZ tarafından geliştirilmiştir.</div>', unsafe_allow_html=True)
