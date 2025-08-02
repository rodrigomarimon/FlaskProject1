from flask import Flask, render_template, request, redirect, url_for, session
from folium.plugins import HeatMap
import pandas as pd
import folium
import os
from werkzeug.utils import secure_filename
import platform
import io
from base64 import b64encode
import sqlite3

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}


app = Flask(__name__)

app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifique as credenciais do usuário (pode ser uma comparação simples por enquanto)
        if username == 'admin' and password == 'admin':
            # Defina uma sessão para indicar que o usuário está logado
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')

    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

df = pd.DataFrame()
intervalo_minutos = 3

def preprocessar_arquivo(caminho_entrada):
    """
    Pré-processa o arquivo CSV para garantir formato consistente
    """
    try:
        # Criar diretório temporário se não existir
        temp_dir = os.path.join(os.path.dirname(caminho_entrada), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Criar nome para arquivo temporário
        nome_arquivo = os.path.basename(caminho_entrada)
        caminho_saida = os.path.join(temp_dir, f'proc_{nome_arquivo}')

        print(f"Pré-processando arquivo {caminho_entrada}")

        with open(caminho_entrada, 'r', encoding='ISO-8859-1') as entrada, \
             open(caminho_saida, 'w', encoding='ISO-8859-1') as saida:

            # Ler primeira linha para identificar cabeçalho
            primeira_linha = entrada.readline().strip()

            # Se a primeira linha não tem vírgulas mas tem espaços, converter para CSV
            if ',' not in primeira_linha and ' ' in primeira_linha:
                saida.write(','.join(primeira_linha.split()) + '\n')
                for linha in entrada:
                    saida.write(','.join(linha.strip().split()) + '\n')
            else:
                # Se já estiver no formato CSV, apenas copiar
                saida.write(primeira_linha + '\n')
                for linha in entrada:
                    saida.write(linha)

        print(f"Arquivo pré-processado salvo em {caminho_saida}")
        return caminho_saida

    except Exception as e:
        print(f"Erro no pré-processamento: {str(e)}")
        return caminho_entrada

def carregar_dataframe_csv(caminho):
    try:
        print(f'Tentando carregar o arquivo CSV: {caminho}')

        # Primeiro, vamos ler algumas linhas do arquivo para análise
        with open(caminho, 'r', encoding='ISO-8859-1') as file:
            primeiras_linhas = [next(file) for _ in range(5)]
        print("Primeiras linhas do arquivo:")
        for linha in primeiras_linhas:
            print(linha.strip())

        # Tentar diferentes métodos de leitura
        try:
            # Primeira tentativa: ler normalmente com vírgula como separador
            df = pd.read_csv(caminho, encoding='ISO-8859-1', sep=',')
        except:
            try:
                # Segunda tentativa: ler com ponto e vírgula como separador
                df = pd.read_csv(caminho, encoding='ISO-8859-1', sep=';')
            except:
                try:
                    # Terceira tentativa: ler com tabulação como separador
                    df = pd.read_csv(caminho, encoding='ISO-8859-1', sep='\t')
                except:
                    # Última tentativa: ler e depois dividir a primeira coluna
                    df = pd.read_csv(caminho, encoding='ISO-8859-1', header=None)
                    if len(df.columns) == 1:
                        # Se tudo está em uma única coluna, dividir pelos delimitadores
                        primeira_coluna = df[0].str.split(',')
                        if primeira_coluna.iloc[0] is not None:
                            colunas = primeira_coluna.iloc[0]
                            df = pd.DataFrame([x.split(',') for x in df[0]], columns=colunas)

        print("Colunas encontradas:", df.columns.tolist())
        print("Primeiras linhas após leitura inicial:")
        print(df.head())

        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()

        # Converter coordenadas
        def convert_coordinate(value):
            if isinstance(value, str):
                # Primeiro substitui vírgula por ponto se for string
                return float(str(value).replace(',', '.'))
            return float(value)

        # Converter coordenadas
        for col in ['Latitude', 'Longitude']:
            if col in df.columns:
                df[col] = df[col].apply(convert_coordinate)

        # Converter velocidade
        if 'Velocidade' in df.columns:
            df['Velocidade'] = df['Velocidade'].apply(convert_coordinate)

        # Processar Data e Hora
        if 'Data' in df.columns and 'Hora' in df.columns:
            print("Processando colunas Data e Hora...")

            # Garantir formato correto da hora
            def format_hora(hora):
                if isinstance(hora, str):
                    partes = hora.strip().split(':')
                    if len(partes) == 2:
                        return f"{hora}:00"
                    return hora
                return "00:00:00"

            df['Hora'] = df['Hora'].apply(format_hora)

            # Criar DataHora
            df['DataHora'] = pd.to_datetime(
                df['Data'] + ' ' + df['Hora'],
                format='%d/%m/%Y %H:%M:%S'
            )

        # Selecionar colunas necessárias
        colunas_necessarias = ['Placa', 'Data', 'Hora', 'Velocidade', 'Latitude', 'Longitude', 'DataHora']
        colunas_presentes = [col for col in colunas_necessarias if col in df.columns]
        df = df[colunas_presentes]

        print("DataFrame processado com sucesso")
        print("Formato final das colunas:")
        print(df.dtypes)
        print("\nPrimeiras linhas do DataFrame processado:")
        print(df.head())

        return df

    except Exception as e:
        import traceback
        print(f'Erro ao carregar arquivo CSV: {str(e)}')
        print("Traceback completo:")
        print(traceback.format_exc())
        return pd.DataFrame()

# def carregar_dataframe_csv(caminho):
#     try:
#         print(f'tentando carregar o arquivo CSV {caminho}')
#         global df
#         extensao = os.path.splitext(caminho)[1].lower()
#         if extensao == '.csv':
#             df = pd.read_csv(caminho, encoding='ISO-8859-1')
#         elif extensao == '.xlsx' or extensao == '.xls':
#             df = pd.read_excel(caminho)
#         else:
#             raise ValueError("Formato de arquivo não suportado")
#         # se for arquivo movida, vai entar aqui
#         if 'HR Evento' in df.columns:
#             print("IDENTIFICADO ARQUIVO MOVIDA")
#             # Converter a coluna 'HR Evento' para tipo datetime, especificando o formato correto
#             df['HR Evento'] = pd.to_datetime(df['HR Evento'], format='%d/%m/%Y %H:%M')

#             # Separar a coluna 'HR Evento' em duas colunas: Data e Hora
#             df['Data'] = df['HR Evento'].dt.strftime('%d/%m/%Y')
#             df['Hora'] = df['HR Evento'].dt.strftime('%H:%M:%S')

#             df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')

#             # Dividir a coluna 'Lat/Long' em duas colunas: Latitude e Longitude
#             df[['Latitude', 'Longitude']] = df['Lat/Long'].str.split(',', expand=True)

#             # Converta as colunas 'Latitude' e 'Longitude' para float
#             df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
#             df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)


#             # Selecionar e reordenar as colunas desejadas
#             df = df[['Placa', 'Data', 'Hora', 'Velocidade', 'Latitude', 'Longitude', 'DataHora']]
#         # se for arquivo localiza, vai entrar aqui
#         else:
#             print("IDENTIFICADO ARQUIVO LOCALIZA")

#             df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')

#             # Converta as colunas 'Latitude' e 'Longitude' para float
#             df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
#             df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)

#             # Verifique se a coluna 'DataHora' foi criada com sucesso
#             if 'DataHora' not in df.columns:
#                 raise ValueError("A coluna 'DataHora' não foi criada com sucesso.")

#         print("DataFrame carregado com sucesso")
#         print(df.head())

#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo CSV: {e}')
#         return pd.DataFrame()
# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     print("entrou na função criar_mapa")
#     if 'DataHora' not in df_filtrado.columns:
#         print("A coluna 'DataHora' não está presente no DataFrame")
#         return None

#     # Criando camadas para cada dia
#     layers = {}
#     for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(), freq='D'):
#         layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))

#     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)

#     # Adicionando camadas ao mapa
#     for layer_name, layer in layers.items():
#         layer.add_to(mapa)

#     # Adicionando camada para o estilo de satélite do Google Maps
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Maps Hybrid', name='Google Maps (Hybrid)').add_to(mapa)

#     # Criando camada para HeatMap
#     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#     HeatMap(dados_heatmap).add_to(mapa)

#     tempo_anterior = None

#     trajeto_layer = folium.FeatureGroup(name='Trajeto')
#     coordenadas = []

#     # Iterando sobre os dados com intervalo_minutos
#     for _, row in df_filtrado.iterrows():
#         coordenadas.append([row['Latitude'], row['Longitude']])
#         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#             latitude, longitude = row['Latitude'], row['Longitude']
#             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"

#             marker = folium.Marker(location=[latitude, longitude],
#                                     popup=folium.Popup(popup_content, max_width=300)
#                                     ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])

#             tempo_anterior = row['DataHora']

#             folium.PolyLine(coordenadas, color="red", weight=2.5, opacity=1).add_to(trajeto_layer)
#             # Adicionando a camada de trajeto ao mapa
#             trajeto_layer.add_to(mapa)

#     # Adicionando controle de camadas ao mapa
#     folium.LayerControl().add_to(mapa)

#     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#     mapa.save(caminho_mapa)

#     return caminho_mapa

# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     try:
#         print("entrou na função criar_mapa")
#         if df_filtrado is None or df_filtrado.empty:
#             print("DataFrame vazio ou None")
#             return None, "DataFrame vazio ou None"

#         if 'DataHora' not in df_filtrado.columns:
#             print("A coluna 'DataHora' não está presente no DataFrame")
#             return None, "A coluna 'DataHora' não está presente no DataFrame"

#         # Criando camadas para cada dia
#         layers = {}
#         for data in pd.date_range(start=df_filtrado['DataHora'].min().date(),
#                                 end=df_filtrado['DataHora'].max().date(),
#                                 freq='D'):
#             layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))

#         # Verificar se há dados válidos para latitude e longitude
#         if pd.isna(df_filtrado.iloc[0]['Latitude']) or pd.isna(df_filtrado.iloc[0]['Longitude']):
#             return None, "Dados de latitude ou longitude inválidos"

#         mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'],
#                                   df_filtrado.iloc[0]['Longitude']],
#                          zoom_start=14)

#         # Adicionando camadas ao mapa
#         for layer_name, layer in layers.items():
#             layer.add_to(mapa)

#         # Adicionando camada para o estilo de satélite do Google Maps
#         folium.TileLayer(
#             'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
#             attr='Google Maps Hybrid',
#             name='Google Maps (Hybrid)'
#         ).add_to(mapa)

#         # Criando camada para HeatMap
#         df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#         dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#         HeatMap(dados_heatmap).add_to(mapa)

#         tempo_anterior = None
#         trajeto_layer = folium.FeatureGroup(name='Trajeto')
#         coordenadas = []

#         # Iterando sobre os dados com intervalo_minutos
#         for _, row in df_filtrado.iterrows():
#             coordenadas.append([row['Latitude'], row['Longitude']])
#             if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#                 latitude, longitude = row['Latitude'], row['Longitude']
#                 google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#                 popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"

#                 marker = folium.Marker(
#                     location=[latitude, longitude],
#                     popup=folium.Popup(popup_content, max_width=300)
#                 ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])

#                 tempo_anterior = row['DataHora']

#         folium.PolyLine(coordenadas, color="red", weight=2.5, opacity=1).add_to(trajeto_layer)
#         trajeto_layer.add_to(mapa)

#         # Adicionando controle de camadas ao mapa
#         folium.LayerControl().add_to(mapa)

#         try:
#             os.makedirs('static', exist_ok=True)
#             caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#             mapa.save(caminho_mapa)
#             return caminho_mapa, None
#         except Exception as e:
#             print(f"Erro ao salvar mapa: {e}")
#             return None, f"Erro ao salvar mapa: {e}"

#     except Exception as e:
#         print(f"Erro ao criar mapa: {e}")
#         return None, f"Erro ao criar mapa: {e}"

def criar_mapa(df_filtrado, intervalo_minutos=3):
    try:
        print("\n=== INÍCIO DA FUNÇÃO CRIAR_MAPA ===")

        if df_filtrado is None or df_filtrado.empty:
            raise ValueError("DataFrame vazio ou None")

        # Verificar dados necessários
        required_columns = ['DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']
        missing_columns = [col for col in required_columns if col not in df_filtrado.columns]
        if missing_columns:
            raise ValueError(f"Colunas ausentes: {missing_columns}")

        # Criar mapa base
        centro_lat = df_filtrado['Latitude'].mean()
        centro_lon = df_filtrado['Longitude'].mean()
        mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=14)

        # Adicionar camada de satélite
        folium.TileLayer(
            'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google Maps Hybrid',
            name='Google Maps (Hybrid)'
        ).add_to(mapa)

        # Criando camada para HeatMap
        df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
        dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
        HeatMap(dados_heatmap).add_to(mapa)

        # tempo_anterior = None
        # trajeto_layer = folium.FeatureGroup(name='Trajeto')
        # coordenadas = []


        # Criar camadas por dia
        layers = {}
        for data in df_filtrado['DataHora'].dt.date.unique():
            layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
            layers[data.strftime('%d/%m/%Y')].add_to(mapa)

        # Adicionar marcadores e trajeto
        tempo_anterior = None
        trajeto_layer = folium.FeatureGroup(name='Trajeto')
        coordenadas = []

        for _, row in df_filtrado.iterrows():
            try:
                lat, lon = float(row['Latitude']), float(row['Longitude'])
                coordenadas.append([lat, lon])

                if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
                    data_str = row['DataHora'].strftime('%d/%m/%Y')

                    popup_content = (
                        f"Placa: {row['Placa']}<br>"
                        f"Data: {data_str}<br>"
                        f"Hora: {row['DataHora'].strftime('%H:%M:%S')}<br>"
                        f"Velocidade: {row['Velocidade']} km/h<br>"
                        f"<a href='https://www.google.com/maps/search/?api=1&query={lat},{lon}' target='_blank'>Ver no Google Maps</a>"
                    )

                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_content, max_width=300)
                    ).add_to(layers[data_str])

                    tempo_anterior = row['DataHora']
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue

        # Adicionar linha do trajeto
        if coordenadas:
            folium.PolyLine(
                coordenadas,
                color="red",
                weight=2.5,
                opacity=1
            ).add_to(trajeto_layer)
            trajeto_layer.add_to(mapa)

        # Adicionar controle de camadas
        folium.LayerControl().add_to(mapa)

        # Salvar mapa
        os.makedirs('static', exist_ok=True)
        caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
        mapa.save(caminho_mapa)

        print("Mapa criado com sucesso")
        return caminho_mapa, None

    except Exception as e:
        import traceback
        print(f"Erro ao criar mapa: {str(e)}")
        print("Traceback completo:")
        print(traceback.format_exc())
        return None, str(e)


from flask import send_from_directory


@app.route('/mapa_gerado/<filename>')
def mapa_gerado(filename):
    # Retorne o arquivo HTML gerado para download
    return send_from_directory('static', filename)


@app.route('/mapa_deslocamento')
def mapa_deslocamento():
    return render_template('mapa_deslocamento.html')
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     print("entrou na funçao index")
#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))

#     global df

#     mapa_gerado = False
#     caminho_mapa = None

#     if request.method == 'POST':
#         print("Método POST detectado")
#         print("Dados do formulário:")
#         print(request.form)
#         print("Arquivos enviados:")
#         print(request.files)
#         data_inicial = request.form['data_inicial']
#         hora_inicial = request.form['hora_inicial']
#         data_final = request.form['data_final']
#         hora_final = request.form['hora_final']

#         if not all([data_inicial, hora_inicial, data_final, hora_final]):
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Forneça todas datas e horas")
#         if 'arquivo_csv' not in request.files:
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")

#         file = request.files['arquivo_csv']

#         if file.filename == '':
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
#             os.makedirs('static', exist_ok=True)

#             # Certifique-se de que o diretório 'uploads' exista

#             df = carregar_dataframe_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             print(df.head)
#             print("linha 242")
#             if 'DataHora' in df.columns:
#                 filtro = ((df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}', format='%Y-%m-%d %H:%M:%S')) &
#                         (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}', format='%Y-%m-%d %H:%M:%S')))
#                 df_filtrado = df[filtro].copy()
#                 print(df_filtrado)

#                 if df_filtrado.empty:
#                     return render_template('index.html', mapa_gerado=False, mensagem_erro=f"Não há dados no intervalo de datas especificado: {data_inicial} {hora_inicial} - {data_final} {hora_final}")

#                 caminho_mapa = criar_mapa(df_filtrado)
#             else:
#                 caminho_mapa = criar_mapa(df)
#             mapa_gerado = True
#     if mapa_gerado:
#         link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
#     else:
#         link_download = None

#     return render_template('index.html', mapa_gerado=mapa_gerado, caminho_mapa=caminho_mapa, link_download=link_download)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("entrou na funçao index")
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    global df
    mapa_gerado = False
    caminho_mapa = None
    mensagem_erro = None

    if request.method == 'POST':
        try:
            print("Método POST detectado")
            print("Dados do formulário:", request.form)
            print("Arquivos enviados:", request.files)

            # Validar dados do formulário
            data_inicial = request.form.get('data_inicial')
            hora_inicial = request.form.get('hora_inicial')
            data_final = request.form.get('data_final')
            hora_final = request.form.get('hora_final')

            if not all([data_inicial, hora_inicial, data_final, hora_final]):
                return render_template('index.html',
                                    mapa_gerado=False,
                                    mensagem_erro="Forneça todas datas e horas")

            if 'arquivo_csv' not in request.files:
                return render_template('index.html',
                                    mapa_gerado=False,
                                    mensagem_erro="Nenhum arquivo enviado")

            file = request.files['arquivo_csv']
            if file.filename == '':
                return render_template('index.html',
                                    mapa_gerado=False,
                                    mensagem_erro="Nenhum arquivo selecionado")

            # Aqui é onde você deve inserir o novo código
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Pré-processar o arquivo
                processed_filepath = preprocessar_arquivo(filepath)

                # Carregar o arquivo processado
                df = carregar_dataframe_csv(processed_filepath)
                if df.empty:
                    return render_template('index.html',
                                        mapa_gerado=False,
                                        mensagem_erro="Erro ao carregar arquivo")

                if 'DataHora' in df.columns:
                    filtro = (
                        (df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}')) &
                        (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}'))
                    )
                    df_filtrado = df[filtro].copy()

                    if df_filtrado.empty:
                        return render_template('index.html',
                                            mapa_gerado=False,
                                            mensagem_erro=f"Não há dados no intervalo especificado")

                    caminho_mapa, erro = criar_mapa(df_filtrado)
                    if erro:
                        return render_template('index.html',
                                            mapa_gerado=False,
                                            mensagem_erro=erro)
                    mapa_gerado = True
                else:
                    caminho_mapa, erro = criar_mapa(df)
                    if erro:
                        return render_template('index.html',
                                            mapa_gerado=False,
                                            mensagem_erro=erro)
                    mapa_gerado = True

        except Exception as e:
            print(f"Erro no processamento: {e}")
            import traceback
            traceback.print_exc()
            return render_template('index.html',
                                mapa_gerado=False,
                                mensagem_erro=f"Erro no processamento: {str(e)}")

    if mapa_gerado and caminho_mapa:
        link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
    else:
        link_download = None

    return render_template('index.html',
                         mapa_gerado=mapa_gerado,
                         caminho_mapa=caminho_mapa,
                         link_download=link_download,
                         mensagem_erro=mensagem_erro)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def abrir_mapa_no_navegador():
    # Determine o sistema operacional:
    sistema_operacional = platform.system()

    # caminho do arquyivo html gerado:
    caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')

    # abra o arquivo no navegador padrão combase no sistema operacional
    if sistema_operacional == 'Windows':
        os.startfile(caminho_arquivo_html)
    elif sistema_operacional =='Linux':
        os.system('xdg-open' + caminho_arquivo_html)
    else:
        print('Sistema operacional não suportado')

# abrir_mapa_no_navegador()