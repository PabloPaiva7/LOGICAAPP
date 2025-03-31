import streamlit as st
import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF

# Configurações de autenticação
USUARIOS = {
    "joao": {"senha": "lider123", "cargo": "lider", "nome": "Líder João", "id": "1"},
    "maria": {"senha": "col123", "cargo": "colaborador", "nome": "Colaborador Maria", "id": "2"},
    "pedro": {"senha": "col123", "cargo": "colaborador", "nome": "Colaborador Pedro", "id": "3"},
    "ana": {"senha": "col123", "cargo": "colaborador", "nome": "Colaborador Ana", "id": "4"},
    "carlos": {"senha": "col123", "cargo": "colaborador", "nome": "Colaborador Carlos", "id": "5"}
}

# Inicialização do estado da sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = None

# Função de login
def fazer_login(username, password):
    if username in USUARIOS and USUARIOS[username]["senha"] == password:
        st.session_state.autenticado = True
        st.session_state.usuario_atual = USUARIOS[username]
        return True
    return False

# Tela de login
if not st.session_state.autenticado:
    st.title("🔐 Login do Sistema")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuário")
    with col2:
        password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if fazer_login(username, password):
            st.success(f"Bem-vindo(a), {st.session_state.usuario_atual['nome']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")
    
    st.info("Usuários disponíveis: joao, maria, pedro, ana, carlos\nSenha para líder: lider123\nSenha para colaboradores: col123")
    st.stop()

# Inicialização das estruturas de dados
if "demandas" not in st.session_state:
    st.session_state.demandas = []
if "historico" not in st.session_state:
    st.session_state.historico = []

# Definição dos tipos de demanda
TIPOS_DEMANDA = [
    "Solicitação de Boleto",
    "Retorno de Análise",
    "Proposta",
    "Minuta",
    "Procuração",
    "Contato do Cliente"
]

# Simulação de usuários
usuarios = {
    "1": "Líder João",
    "2": "Colaborador Maria",
    "3": "Colaborador Pedro",
    "4": "Colaborador Ana",
    "5": "Colaborador Carlos"
}

# Função para registrar atividade no histórico
def registrar_atividade(demanda, acao, usuario):
    st.session_state.historico.append({
        "data_hora": datetime.now(),
        "demanda_id": demanda["id"],
        "titulo_demanda": demanda["titulo"],
        "tipo_demanda": demanda["tipo"],
        "acao": acao,
        "usuario": usuarios[usuario],
        "status": demanda["status"]
    })

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Demandas",
    page_icon="📋",
    layout="wide"
)

# Adicionar botão de logout no canto superior direito
if st.session_state.autenticado:
    col_logout = st.columns([8, 2])  # Cria duas colunas, uma maior e uma menor
    with col_logout[1]:  # Usa a coluna menor para o botão de logout
        if st.button("🚪 Logout", type="primary"):
            st.session_state.autenticado = False
            st.session_state.usuario_atual = None
            st.rerun()

# Sidebar para criar demanda
st.sidebar.header("🆕 Criar Nova Demanda")
with st.sidebar:
    titulo = st.text_input("Título da Demanda")
    descricao = st.text_area("Descrição")
    
    tipo_demanda = st.selectbox(
        "Tipo de Demanda",
        options=TIPOS_DEMANDA,
        help="Selecione o tipo da demanda"
    )
    
    colaborador_id = st.selectbox(
        "Atribuir a:",
        list(usuarios.keys()),
        format_func=lambda x: usuarios[x]
    )
    
    prioridade = st.select_slider(
        "Prioridade",
        options=["Baixa", "Média", "Alta"],
        value="Média"
    )
    
    # Modificar o date_input para formato brasileiro
    data_limite = st.date_input(
        "Data Limite",
        format="DD/MM/YYYY"  # Formato brasileiro
    )

    if st.button("📝 Criar Demanda"):
        nova_demanda = {
            "id": len(st.session_state.demandas) + 1,
            "titulo": titulo,
            "descricao": descricao,
            "tipo": tipo_demanda,
            "status": "pendente",
            "lider_id": "1",
            "colaborador_id": colaborador_id,
            "confirmacao_lider": False,
            "prioridade": prioridade,
            "data_criacao": datetime.now(),
            "data_limite": data_limite,
            "data_conclusao": None
        }
        st.session_state.demandas.append(nova_demanda)
        registrar_atividade(nova_demanda, "criação", "1")
        st.success("✅ Demanda criada com sucesso!")

# Corpo principal
st.title("📋 Sistema de Gestão de Demandas")

# Abas principais
aba = st.tabs(["📝 Minhas Demandas", "✅ Confirmar Conclusão", "📊 Histórico", "📈 Dashboard"])

# Na Aba 1: Minhas Demandas
with aba[0]:
    if not st.session_state.autenticado:
        st.warning("⚠️ Por favor, faça login para visualizar suas demandas.")
    else:
        # Usar diretamente o usuário logado
        usuario_atual = st.session_state.usuario_atual['id']
        st.write(f"👤 Usuário atual: {st.session_state.usuario_atual['nome']}")
        
        demandas_usuario = [d for d in st.session_state.demandas if d["colaborador_id"] == usuario_atual]
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_status = st.multiselect(
                "Status:",
                ["pendente", "concluído", "confirmado"],
                default=["pendente"]
            )
        with col2:
            filtro_prioridade = st.multiselect(
                "Prioridade:",
                ["Baixa", "Média", "Alta"],
                default=["Alta", "Média", "Baixa"]
            )
        with col3:
            filtro_tipo = st.multiselect(
                "Tipo de Demanda:",
                TIPOS_DEMANDA,
                default=TIPOS_DEMANDA
            )
        
        # Aplicar filtros
        demandas_filtradas = [
            d for d in demandas_usuario
            if d["status"] in filtro_status
            and d["prioridade"] in filtro_prioridade
            and d["tipo"] in filtro_tipo
        ]
        
        # Mostrar demandas filtradas
        for demanda in demandas_filtradas:
            if demanda["status"] == "pendente":
                st.warning("⚠️ Você tem demandas pendentes!")
            elif demanda["status"] == "concluído":
                st.success("✅ Você tem demandas concluídas!")
            elif demanda["status"] == "confirmado":
                st.success("✔️ Você tem demandas confirmadas!")
        
        # Mostrar detalhes das demandas
        for demanda in demandas_filtradas:
            with st.expander(f"📌 {demanda['titulo']} - {demanda['status'].upper()}"):
                st.write(f"📝 Descrição: {demanda['descricao']}")
                st.write(f"📋 Tipo: {demanda['tipo']}")
                st.write(f"⚡ Prioridade: {demanda['prioridade']}")
                st.write(f"📅 Data Limite: {demanda['data_limite'].strftime('%d/%m/%Y')}")
                
                # Mostrar observação de devolução se existir
                if demanda.get("observacao_devolucao"):
                    st.error(f"⚠️ Demanda devolvida: {demanda['observacao_devolucao']}")
                
                if demanda["status"] == "pendente":
                    if st.button("✅ Concluir", key=f"done_{demanda['id']}"):
                        demanda["status"] = "concluído"
                        demanda["data_conclusao"] = datetime.now()
                        registrar_atividade(demanda, "conclusão", usuario_atual)
                        st.success("Demanda concluída!")
                        st.rerun()

# Na Aba 2: Confirmar Conclusão
with aba[1]:
    if not st.session_state.autenticado:
        st.warning("⚠️ Por favor, faça login para visualizar esta seção.")
    else:
        # Verificar se é líder
        if st.session_state.usuario_atual["cargo"] == "lider":
            st.subheader("✅ Confirmação de Demandas")
            
            demandas_concluidas = [
                d for d in st.session_state.demandas
                if d["status"] == "concluído" and not d.get("confirmacao_lider", False)
            ]
            
            if not demandas_concluidas:
                st.info("Não há demandas aguardando confirmação.")
            else:
                for demanda in demandas_concluidas:
                    with st.expander(f"✅ {demanda['titulo']} - Aguardando Confirmação"):
                        st.write(f"📝 Descrição: {demanda['descricao']}")
                        st.write(f"📋 Tipo: {demanda['tipo']}")
                        st.write(f"👤 Responsável: {usuarios[demanda['colaborador_id']]}")
                        st.write(f"📅 Concluído em: {demanda['data_conclusao'].strftime('%d/%m/%Y %H:%M')}")
                        
                        # Campo para observações de devolução
                        obs_key = f"obs_{demanda['id']}"
                        observacao = st.text_area(
                            "Observações (necessário para devolver):",
                            key=obs_key,
                            help="Preencha se precisar devolver a demanda"
                        )
                        
                        # Botões de ação
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✔️ Confirmar", key=f"confirm_{demanda['id']}"):
                                demanda["status"] = "confirmado"
                                demanda["confirmacao_lider"] = True
                                registrar_atividade(
                                    demanda, 
                                    "confirmação", 
                                    st.session_state.usuario_atual["id"]
                                )
                                st.success("Demanda confirmada com sucesso!")
                                st.rerun()
                        
                        with col2:
                            if st.button("❌ Devolver", 
                                       key=f"return_{demanda['id']}", 
                                       type="secondary"):
                                if observacao.strip():
                                    demanda["status"] = "pendente"
                                    demanda["confirmacao_lider"] = False
                                    demanda["data_conclusao"] = None
                                    demanda["observacao_devolucao"] = observacao
                                    registrar_atividade(
                                        demanda, 
                                        f"devolução: {observacao}", 
                                        st.session_state.usuario_atual["id"]
                                    )
                                    st.error("Demanda devolvida para revisão!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Por favor, adicione uma observação para devolver.")
        else:
            st.warning("⚠️ Apenas o líder pode acessar esta seção.")

# ...existing code...



# Aba 3: Histórico
with aba[2]:
    st.subheader("📊 Histórico de Atividades")
    
    # Filtros do histórico
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        filtro_usuario_hist = st.multiselect(
            "Filtrar por Usuário:",
            options=["Todos"] + list(usuarios.values()),
            default="Todos"
        )
    
    with col_hist2:
        filtro_tipo_hist = st.multiselect(
            "Filtrar por Tipo:",
            options=["Todos"] + TIPOS_DEMANDA,
            default="Todos"
        )
    
    historico_filtrado = st.session_state.historico.copy()
    
    if "Todos" not in filtro_usuario_hist:
        historico_filtrado = [
            h for h in historico_filtrado
            if h["usuario"] in filtro_usuario_hist
        ]
    
    if "Todos" not in filtro_tipo_hist:
        historico_filtrado = [
            h for h in historico_filtrado
            if h["tipo_demanda"] in filtro_tipo_hist
        ]
    
    historico_ordenado = sorted(
        historico_filtrado,
        key=lambda x: x["data_hora"],
        reverse=True
    )
    
    for registro in historico_ordenado:
        with st.expander(
            f"🕒 {registro['data_hora'].strftime('%d/%m/%Y %H:%M')} - {registro['titulo_demanda']}"
        ):
            st.write(f"👤 Usuário: {registro['usuario']}")
            st.write(f"📋 Tipo: {registro['tipo_demanda']}")
            st.write(f"🔄 Ação: {registro['acao']}")
            st.write(f"📌 Status: {registro['status']}")

# Aba 4: Dashboard
with aba[3]:
    st.subheader("📈 Dashboard de Desempenho")
    
    # Filtros do Dashboard
    col_filtros1, col_filtros2, col_filtros3 = st.columns(3)
    
    with col_filtros1:
        filtro_colaborador = st.multiselect(
            "👥 Colaboradores:",
            options=["Todos"] + list(usuarios.values()),
            default="Todos"
        )
    
    with col_filtros2:
        filtro_tipo_dash = st.multiselect(
            "📋 Tipos de Demanda:",
            options=["Todos"] + TIPOS_DEMANDA,
            default="Todos"
        )
    
    with col_filtros3:
        filtro_periodo = st.date_input(
            "📅 Período:",
            value=(datetime.now().date(), datetime.now().date()),
            format="DD/MM/YYYY",  # Formato brasileiro
        )

    # Aplicar filtros
    demandas_filtradas_dash = st.session_state.demandas.copy()
    
    if "Todos" not in filtro_colaborador:
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if usuarios[d["colaborador_id"]] in filtro_colaborador
        ]
    
    if "Todos" not in filtro_tipo_dash:
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if d["tipo"] in filtro_tipo_dash
        ]
    
    if isinstance(filtro_periodo, tuple):
        inicio, fim = filtro_periodo
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if inicio <= d["data_criacao"].date() <= fim
        ]

    # Métricas Gerais
    st.subheader("📊 Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    
    total_filtrado = len(demandas_filtradas_dash)
    concluidas_filtrado = len([d for d in demandas_filtradas_dash if d["status"] == "concluído"])
    taxa_conclusao = (concluidas_filtrado / total_filtrado * 100) if total_filtrado > 0 else 0
    
    with col1:
        st.metric("Total de Demandas", total_filtrado)
    with col2:
        st.metric("Concluídas", concluidas_filtrado)
    with col3:
        st.metric("Taxa de Conclusão", f"{taxa_conclusao:.1f}%")

    # Análise por Colaborador
    st.subheader("👥 Desempenho por Colaborador")
    
    dados_colaboradores = []
    for col_id, col_nome in usuarios.items():
        demandas_col = [d for d in demandas_filtradas_dash if d["colaborador_id"] == col_id]
        total_col = len(demandas_col)
        concluidas_col = len([d for d in demandas_col if d["status"] == "concluído"])
        taxa_col = (concluidas_col / total_col * 100) if total_col > 0 else 0
        pendentes_col = total_col - concluidas_col
        
        dados_colaboradores.append({
            "Colaborador": col_nome,
            "Total de Demandas": total_col,
            "Concluídas": concluidas_col,
            "Pendentes": pendentes_col,
            "Taxa de Conclusão": f"{taxa_col:.1f}%"
        })
    
    df_colaboradores = pd.DataFrame(dados_colaboradores)
    st.dataframe(df_colaboradores, use_container_width=True)

    # Análise por Tipo
    st.subheader("📋 Demandas por Tipo")
    dados_tipos = []
    for tipo in TIPOS_DEMANDA:
        demandas_tipo = [d for d in demandas_filtradas_dash if d["tipo"] == tipo]
        total_tipo = len(demandas_tipo)
        concluidas_tipo = len([d for d in demandas_tipo if d["status"] == "concluído"])
        taxa_tipo = (concluidas_tipo / total_tipo * 100) if total_tipo > 0 else 0
        pendentes_tipo = total_tipo - concluidas_tipo
        
        dados_tipos.append({
            "Tipo": tipo,
            "Total": total_tipo,
            "Concluídas": concluidas_tipo,
            "Pendentes": pendentes_tipo,
            "Taxa de Conclusão": f"{taxa_tipo:.1f}%"
        })
    
    df_tipos = pd.DataFrame(dados_tipos)
    st.dataframe(df_tipos, use_container_width=True)

    # Resumo do Período
    if total_filtrado > 0:
        st.subheader("📅 Resumo do Período")
        col_resumo1, col_resumo2 = st.columns(2)
        
        with col_resumo1:
            st.info(f"⏰ Período: {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}")
        
        with col_resumo2:
            media_diaria = total_filtrado / max((fim - inicio).days + 1, 1)
            st.info(f"📊 Média diária: {media_diaria:.1f} demandas")
    else:
        st.info("Não há dados para o período selecionado")


        # Seção de Download de Relatórios
    st.subheader("📥 Download de Relatórios")
    
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        formato_download = st.selectbox(
            "📁 Formato do Relatório:",
            ["CSV"],
            help="Escolha o formato para download"
        )
    
    with col_download2:
        tipo_relatorio = st.selectbox(
            "📊 Tipo de Relatório:",
            ["Completo", "Resumido"],
            help="Escolha o nível de detalhamento"
        )


    def preparar_dados_csv(demandas, tipo):
        if tipo == "Completo":
            dados = []
            for d in demandas:
                dados.append({
                    "Data Criação": d["data_criacao"].strftime("%d/%m/%Y %H:%M"),
                    "Título": d["titulo"],
                    "Tipo": d["tipo"],
                    "Descrição": d["descricao"],
                    "Status": d["status"].upper(),
                    "Prioridade": d["prioridade"],
                    "Responsável": usuarios[d["colaborador_id"]],
                    "Data Limite": d["data_limite"].strftime("%d/%m/%Y"),
                    "Data Conclusão": d["data_conclusao"].strftime("%d/%m/%Y %H:%M") if d["data_conclusao"] else "Não concluído"
                })
        else:
            dados = [{
                "Métrica": "Total de Demandas",
                "Valor": total_filtrado
            }, {
                "Métrica": "Demandas Concluídas",
                "Valor": concluidas_filtrado
            }, {
                "Métrica": "Taxa de Conclusão",
                "Valor": f"{taxa_conclusao:.1f}%"
            }]
            
            # Adicionar resumo por tipo
            for tipo in TIPOS_DEMANDA:
                total_tipo = len([d for d in demandas if d["tipo"] == tipo])
                dados.append({
                    "Métrica": f"Total {tipo}",
                    "Valor": total_tipo
                })
        
        return pd.DataFrame(dados)

    if st.button("🔄 Gerar Relatório"):
        try:
            # Preparar dados
            if formato_download == "CSV":
                df_relatorio = preparar_dados_csv(demandas_filtradas_dash, tipo_relatorio)
                buffer = io.StringIO()
                df_relatorio.to_csv(buffer, index=False, encoding='utf-8-sig')
                dados_download = buffer.getvalue()
                mime = "text/csv"
                file_extension = "csv"
            
            # Nome do arquivo
            data_atual = datetime.now().strftime("%d-%m-%Y_%H-%M")
            filtro_col_texto = "_".join(filtro_colaborador) if "Todos" not in filtro_colaborador else "Todos"
            nome_arquivo = f"relatorio_demandas_{filtro_col_texto}_{data_atual}.{file_extension}"
            
            # Botão de download
            st.download_button(
                label="⬇️ Baixar Relatório",
                data=dados_download,
                file_name=nome_arquivo,
                mime=mime,
                help="Clique para baixar o relatório gerado"
            )
            
            st.success("✅ Relatório gerado com sucesso!")
            
            # Pré-visualização (apenas para CSV)
            if formato_download == "CSV":
                st.subheader("👁️ Pré-visualização do Relatório")
                st.dataframe(df_relatorio, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")
            st.error("Por favor, tente novamente ou contate o suporte.")