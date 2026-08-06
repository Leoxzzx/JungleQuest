import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import pypdf

# Configuração da página (otimizada para celular e notebook)
st.set_page_config(page_title="IA de Estudos", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.title("🎓 Plataforma de Estudos com IA")

# Configurar API Key na barra lateral
st.sidebar.title("⚙️ Configurações")
api_key = st.sidebar.text_input("Cole sua Gemini API Key aqui:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# Criar Salas por Matéria/Assunto
st.sidebar.subheader("📚 Minhas Salas")
sala = st.sidebar.selectbox(
    "Escolha a Sala / Matéria:", 
    ["Matemática", "Português", "História", "Geografia", "Ciências", "Raciocínio Lógico", "Concursos / Geral"]
)

st.subheader(f"📍 Sala Atual: {sala}")

# Seleção do Nível e Quantidade de Questões
nivel = st.radio(
    "Escolha a quantidade/nível de questões:",
    ["Nível Razoável (10 questões)", "Nível Médio (20 questões)", "Nível Hard (30 questões)"]
)

qtd_questoes = 10 if "10" in nivel else (20 if "20" in nivel else 30)

# Opções de Entrada do Conteúdo
st.write("---")
st.write("### 📥 Enviar Material para Gerar Questões")

tab1, tab2 = st.tabs(["📄 Enviar Arquivo / Texto", "🔗 Link do YouTube"])

conteudo_processado = ""

with tab1:
    arquivo = st.file_uploader("Envie um arquivo PDF ou TXT:", type=["pdf", "txt"])
    texto_direto = st.text_area("Ou cole o texto/resumo aqui se preferir:")
    
    if arquivo:
        if arquivo.name.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(arquivo)
            for page in pdf_reader.pages:
                conteudo_processado += page.extract_text() or ""
        elif arquivo.name.endswith(".txt"):
            conteudo_processado = arquivo.read().decode("utf-8")
        st.success(f"Arquivo '{arquivo.name}' carregado!")
    elif texto_direto:
        conteudo_processado = texto_direto

with tab2:
    link_youtube = st.text_input("Cole o link do vídeo do YouTube:")
    if link_youtube:
        try:
            if "v=" in link_youtube:
                video_id = link_youtube.split("v=")[-1].split("&")[0]
            elif "youtu.be/" in link_youtube:
                video_id = link_youtube.split("youtu.be/")[-1].split("?")[0]
            else:
                video_id = link_youtube

            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
            conteudo_processado = " ".join([i['text'] for i in transcript])
            st.success("Legenda/Transcrição do vídeo extraída com sucesso!")
        except Exception as e:
            st.error("Não foi possível pegar a legenda automaticamente. Certifique-se de que o vídeo possui legendas ativas.")

# Botão de Geração de Questões
st.write("---")
if st.button("🚀 Gerar Questões"):
    if not api_key:
        st.warning("⚠️ Cole sua Gemini API Key na barra lateral para continuar.")
    elif not conteudo_processado:
        st.warning("⚠️ Envie um arquivo, texto ou link do YouTube com o conteúdo da aula.")
    else:
        with st.spinner("⏳ Analisando conteúdo e criando as questões..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Você é um professor preparador de exames e concursos. 
                Com base ESTRITAMENTE no conteúdo fornecido abaixo, crie um simulado contendo exatamente {qtd_questoes} questões de múltipla escolha.
                
                Regras:
                1. Cada questão deve ter 4 alternativas (A, B, C, D).
                2. Apresente primeiro todas as {qtd_questoes} questões.
                3. Ao final do documento, inclua o GABARITO COMENTADO indicando a resposta correta e a explicação de cada uma.
                
                Matéria/Contexto: {sala}
                Nível do Teste: {nivel}
                
                CONTEÚDO BASE PARA CRIAR AS QUESTÕES:
                {conteudo_processado[:15000]}
                """
                
                response = model.generate_content(prompt)
                st.markdown("### 📝 Simulado Gerado")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar as questões: {e}")
              
