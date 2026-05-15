import streamlit as st
import requests
import io
from PIL import Image

# --- РАБОЧИЕ ЭНДПОИНТЫ ---
# Для картинок используем Pollinations
IMAGE_API_URL = "https://image.pollinations.ai/p/"

# Для текста используем Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_HEADERS = {"Authorization": "Bearer YOUR_HF_TOKEN"}

def call_text_model(prompt):
    """Запрос к текстовой модели через Hugging Face"""
    try:
        payload = {
            "inputs": f"<s>[INST] {prompt} [/INST]",
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'Нет ответа').strip()
            return str(result)
        elif response.status_code == 503:
            return "⏳ Модель загружается... Попробуйте через 30 секунд"
        else:
            return f"❌ Ошибка API: {response.status_code}. Проверьте токен HF."
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

def call_image_model(prompt):
    """Генерация картинки через Pollinations"""
    try:
        clean_prompt = prompt.replace("нарисуй", "").replace("создай изображение", "").strip()
        encoded_prompt = requests.utils.quote(clean_prompt)
        final_url = f"{IMAGE_API_URL}{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"

        response = requests.get(final_url, timeout=30)
        if response.status_code == 200 and response.content:
            return Image.open(io.BytesIO(response.content))
        return None
    except Exception as e:
        st.error(f"Ошибка генерации: {str(e)}")
        return None

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="AI Агент", layout="centered")
st.title("🤖 Мультимодальный AI")
st.write("Автоматически определяю: текст или картинку?")

with st.sidebar:
    st.header("⚙️ Настройки")
    hf_token = st.text_input("Hugging Face Token", type="password", 
                            help="Получите бесплатно на huggingface.co/settings/tokens")
    if hf_token:
        HF_HEADERS["Authorization"] = f"Bearer {hf_token}"

user_prompt = st.text_input("Введите запрос:", 
                           placeholder=" Текст: 'Расскажи про космос'\n🎨 Картинка: 'Нарисуй кота в космосе'")

if user_prompt and st.button("Отправить"):
    image_keywords = ["нарисуй", "изображение", "картинка", "фото", "создай изображение", 
                     "draw", "image", "picture", "photo", "visualize", "сгенерируй", "фотографию"]
    is_image_request = any(keyword in user_prompt.lower() for keyword in image_keywords)

    if is_image_request:
        st.info("🎨 Распознан запрос на ИЗОБРАЖЕНИЕ")
        with st.spinner("Генерирую картинку..."):
            img = call_image_model(user_prompt)
            if img:
                st.image(img, caption=user_prompt, use_container_width=True)
                st.success("✅ Готово!")
            else:
                st.error("❌ Не удалось сгенерировать изображение")
    else:
        st.info("📝 Распознан ТЕКСТОВЫЙ запрос")
        if not hf_token:
            st.warning("⚠️ Введите токен Hugging Face в боковой панели!")
        else:
            with st.spinner("Думаю..."):
                text = call_text_model(user_prompt)
                st.write("### Ответ:")
                st.write(text)

st.markdown("---")
st.markdown("**💡 Примеры запросов:**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("📝 **Текст:**\n- Расскажи про ИИ\n- Что такое квантовый компьютер?\n- Напиши стих про весну")
with col2:
    st.markdown("🎨 **Картинки:**\n- Нарисуй дракона\n- Кот в скафандре\n- Футуристический город")
