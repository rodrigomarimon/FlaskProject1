# from flask import Flask, render_template, request, redirect, url_for, session
# from folium.plugins import HeatMap
# import pandas as pd
# import folium
# import os
# from werkzeug.utils import secure_filename
# import platform
# import io
# from base64 import b64encode
# import sqlite3
#
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'csv'}
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
#
# app.config['UPLOAD_FOLDER'] = 'uploads'
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         # Verifique as credenciais do usuário (pode ser uma comparação simples por enquanto)
#         if username == 'admin' and password == 'admin':
#             # Defina uma sessão para indicar que o usuário está logado
#             session['logged_in'] = True
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')
#
#     return render_template('login.html')
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
# df = pd.DataFrame()
# intervalo_minutos = 3
#
#
# def carregar_dataframe_csv(caminho):
#     try:
#         print(f'tentando carregar o arquivo CSV {caminho}')
#         global df
#         df = pd.read_csv(caminho, encoding='ISO-8859-1')
#
#         # Verifique se as colunas 'Data' e 'Hora' existem no DataFrame
#         if 'Data' not in df.columns or 'Hora' not in df.columns:
#             raise ValueError("O arquivo CSV não contém as colunas 'Data' e 'Hora'.")
#
#         # Crie a coluna 'DataHora' a partir das colunas 'Data' e 'Hora'
#         # df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %I:%M:%S %p')
#         df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')
#
#         # Converta as colunas 'Latitude' e 'Longitude' para float
#         df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
#         df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)
#
#         # Verifique se a coluna 'DataHora' foi criada com sucesso
#         if 'DataHora' not in df.columns:
#             raise ValueError("A coluna 'DataHora' não foi criada com sucesso.")
#
#         print("DataFrame carregado com sucesso")
#         print(df.head())
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo CSV: {e}')
#         return pd.DataFrame()
# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     if 'DataHora' not in df_filtrado.columns:
#         print("A coluna 'DataHora' não está presente no DataFrame")
#         return None
#
#     # Criando camadas para cada dia
#     layers = {}
#     for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(), freq='D'):
#         layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
#
#     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
#
#     # Adicionando camadas ao mapa
#     for layer_name, layer in layers.items():
#         layer.add_to(mapa)
#
#     # Adicionando camada para o estilo de satélite do Google Maps
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Hybrid', name='Google Maps (Hybrid)').add_to(mapa)
#
#     # Criando camada para HeatMap
#     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#     HeatMap(dados_heatmap).add_to(mapa)
#
#     tempo_anterior = None
#
#     # Iterando sobre os dados com intervalo_minutos
#     for _, row in df_filtrado.iterrows():
#         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#             latitude, longitude = row['Latitude'], row['Longitude']
#             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
#             marker = folium.Marker(location=[latitude, longitude],
#                                     popup=folium.Popup(popup_content, max_width=300)
#                                     ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])
#
#             tempo_anterior = row['DataHora']
#
#     # Adicionando controle de camadas ao mapa
#     folium.LayerControl().add_to(mapa)
#
#     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#     mapa.save(caminho_mapa)
#
#     return caminho_mapa
#
#
# # def criar_mapa(df_filtrado, intervalo_minutos=3):
# #     if 'DataHora' not in df_filtrado.columns:
# #         print("A coluna 'DataHora' não está presente no DataFrame")
# #         return None
#
# #     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
# #     # folium.TileLayer("cartodbpositron").add_to(mapa)
# #     folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps Satellite', name='Google Maps (Satellite)').add_to(mapa)
# #     # Criando camada para HeatMap
# #     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
# #     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
# #     HeatMap(dados_heatmap).add_to(mapa)
#
# #     # Definindo intervalo de dias
# #     data_inicio = df_filtrado['DataHora'].min().date()
# #     data_fim = df_filtrado['DataHora'].max().date()
#
# #     # Criando camadas para cada dia
# #     for data in pd.date_range(start=data_inicio, end=data_fim, freq='D'):
# #         df_dia = df_filtrado[df_filtrado['DataHora'].dt.date == data.date()]
# #         layer = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
#
# #         for _, row in df_dia.iterrows():
# #             latitude, longitude = row['Latitude'], row['Longitude']
# #             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
# #             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
# #             marker = folium.Marker(location=[latitude, longitude],
# #                                     popup=folium.Popup(popup_content, max_width=300)
# #                                     ).add_to(layer)
#
# #         layer.add_to(mapa)
#
# #     # Adicionando controle de camadas ao mapa
# #     folium.LayerControl().add_to(mapa)
#
# #     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
# #     mapa.save(caminho_mapa)
#
# #     return caminho_mapa
# # def criar_mapa(df_filtrado):
#
# #     print("Função criar_mapa chamada com DataFrame:")
# #     print(df_filtrado)
# #     if 'DataHora' not in df_filtrado.columns:
# #         print("A coluna 'DataHora' não está presente no DataFrame")
# #     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
#
# #     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
# #     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#
# #     HeatMap(dados_heatmap).add_to(mapa)
# #     tempo_anterior = None
#
# #     for _, row in df_filtrado.iterrows():
# #         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
# #             latitude, longitude = row['Latitude'], row['Longitude']
# #             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
# #             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
# #             marker = folium.Marker(location=[latitude, longitude],
# #                                     popup=folium.Popup(popup_content, max_width=300)
# #                                     ).add_to(mapa)
#
# #             tempo_anterior = row['DataHora']
# #     # line_points = df_velocidade_zero[['Latitude', 'Longitude']]
# #     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#
# #     lines_group = folium.FeatureGroup(name="Lines").add_to(mapa)
# #     # lines_group.add_child(folium.PolyLine(locations=line_points, weight=3,color = 'yellow'))
# #     # folium.LayerControl().add_to(mapa)
# #     # folium.TileLayer("cartodbpositron").add_to(mapa)
#
# #     mapa.save(caminho_mapa)
#
# #     return caminho_mapa
# from flask import send_from_directory
#
#
# @app.route('/mapa_gerado/<filename>')
# def mapa_gerado(filename):
#     # Retorne o arquivo HTML gerado para download
#     return send_from_directory('static', filename)
#
#
# @app.route('/mapa_deslocamento')
# def mapa_deslocamento():
#     return render_template('mapa_deslocamento.html')
#
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))
#
#     global df
#
#     mapa_gerado = False
#     caminho_mapa = None
#
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
#
#         if not all([data_inicial, hora_inicial, data_final, hora_final]):
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Forneça todas datas e horas")
#         if 'arquivo_csv' not in request.files:
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         file = request.files['arquivo_csv']
#
#         if file.filename == '':
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
#             os.makedirs('static', exist_ok=True)
#
#             # Certifique-se de que o diretório 'uploads' exista
#
#             df = carregar_dataframe_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#
#             filtro = ((df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}', format='%Y-%m-%d %H:%M:%S')) &
#                     (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}', format='%Y-%m-%d %H:%M:%S')))
#             df_filtrado = df[filtro].copy()
#             print(df_filtrado)
#
#             if df_filtrado.empty:
#                 return render_template('index.html', mapa_gerado=False, mensagem_erro=f"Não há dados no intervalo de datas especificado: {data_inicial} {hora_inicial} - {data_final} {hora_final}")
#
#             caminho_mapa = criar_mapa(df_filtrado)
#             mapa_gerado = True
#     if mapa_gerado:
#         link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
#     else:
#         link_download = None
#
#     return render_template('index.html', mapa_gerado=mapa_gerado, caminho_mapa=caminho_mapa, link_download=link_download)
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('login'))
#
# def abrir_mapa_no_navegador():
#     # Determine o sistema operacional:
#     sistema_operacional = platform.system()
#
#     # caminho do arquyivo html gerado:
#     caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')
#
#     # abra o arquivo no navegador padrão combase no sistema operacional
#     if sistema_operacional == 'Windows':
#         os.startfile(caminho_arquivo_html)
#     elif sistema_operacional =='Linux':
#         os.system('xdg-open' + caminho_arquivo_html)
#     else:
#         print('Sistema operacional não suportado')
#
# # abrir_mapa_no_navegador()
#
#
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, session
# from folium.plugins import HeatMap
# import pandas as pd
# import folium
# import os
# from werkzeug.utils import secure_filename
# import platform
# import io
# from base64 import b64encode
# import sqlite3
#
# UPLOAD_FOLDER = 'uploads'
# # MODIFICAÇÃO 1: Adicionar 'xlsx' às extensões permitidas
# ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
# app.config['UPLOAD_FOLDER'] = 'uploads'
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         if username == 'admin' and password == 'admin':
#             session['logged_in'] = True
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')
#
#     return render_template('login.html')
#
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# df = pd.DataFrame()
# intervalo_minutos = 3
#
#
# # MODIFICAÇÃO 2: Nova função para carregar arquivos XLSX
# def carregar_dataframe_xlsx(caminho):
#     try:
#         print(f'Tentando carregar o arquivo XLSX {caminho}')
#         global df
#         # Lê o arquivo Excel - pode especificar a planilha com sheet_name se necessário
#         df = pd.read_excel(caminho, sheet_name=0)  # sheet_name=0 pega a primeira planilha
#
#         # Verifique se as colunas 'Data' e 'Hora' existem no DataFrame
#         if 'Data' not in df.columns or 'Hora' not in df.columns:
#             raise ValueError("O arquivo XLSX não contém as colunas 'Data' e 'Hora'.")
#
#         # Crie a coluna 'DataHora' a partir das colunas 'Data' e 'Hora'
#         df['DataHora'] = pd.to_datetime(df['Data'].astype(str) + ' ' + df['Hora'].astype(str),
#                                         format='%d/%m/%Y %H:%M:%S', errors='coerce')
#
#         # Se o formato acima não funcionar, tente outros formatos comuns
#         if df['DataHora'].isna().all():
#             try:
#                 df['DataHora'] = pd.to_datetime(df['Data'].astype(str) + ' ' + df['Hora'].astype(str),
#                                                 format='%Y-%m-%d %H:%M:%S', errors='coerce')
#             except:
#                 pass
#
#         # Converta as colunas 'Latitude' e 'Longitude' para float
#         # Para XLSX, pode não precisar da conversão de vírgula para ponto
#         if df['Latitude'].dtype == 'object':
#             df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.').astype(float)
#         else:
#             df['Latitude'] = df['Latitude'].astype(float)
#
#         if df['Longitude'].dtype == 'object':
#             df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.').astype(float)
#         else:
#             df['Longitude'] = df['Longitude'].astype(float)
#
#         # Verifique se a coluna 'DataHora' foi criada com sucesso
#         if 'DataHora' not in df.columns or df['DataHora'].isna().all():
#             raise ValueError("A coluna 'DataHora' não foi criada com sucesso.")
#
#         print("DataFrame XLSX carregado com sucesso")
#         print(df.head())
#         print(f"Colunas disponíveis: {df.columns.tolist()}")
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo XLSX: {e}')
#         return pd.DataFrame()
#
#
# # MODIFICAÇÃO 3: Função unificada para carregar ambos os tipos de arquivo
# def carregar_dataframe(caminho):
#     """
#     Carrega um DataFrame a partir de um arquivo CSV ou XLSX
#     """
#     extensao = caminho.lower().split('.')[-1]
#
#     if extensao == 'csv':
#         return carregar_dataframe_csv(caminho)
#     elif extensao == 'xlsx':
#         return carregar_dataframe_xlsx(caminho)
#     else:
#         raise ValueError(f"Formato de arquivo não suportado: {extensao}")
#
#
# def carregar_dataframe_csv(caminho):
#     try:
#         print(f'Tentando carregar o arquivo CSV {caminho}')
#         global df
#         df = pd.read_csv(caminho, encoding='ISO-8859-1')
#
#         if 'Data' not in df.columns or 'Hora' not in df.columns:
#             raise ValueError("O arquivo CSV não contém as colunas 'Data' e 'Hora'.")
#
#         df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')
#
#         df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
#         df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)
#
#         if 'DataHora' not in df.columns:
#             raise ValueError("A coluna 'DataHora' não foi criada com sucesso.")
#
#         print("DataFrame CSV carregado com sucesso")
#         print(df.head())
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo CSV: {e}')
#         return pd.DataFrame()
#
#
# # Resto do código permanece igual...
# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     if 'DataHora' not in df_filtrado.columns:
#         print("A coluna 'DataHora' não está presente no DataFrame")
#         return None
#
#     layers = {}
#     for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(),
#                               freq='D'):
#         layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
#
#     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
#
#     for layer_name, layer in layers.items():
#         layer.add_to(mapa)
#
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Hybrid',
#                      name='Google Maps (Hybrid)').add_to(mapa)
#
#     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#     HeatMap(dados_heatmap).add_to(mapa)
#
#     tempo_anterior = None
#
#     for _, row in df_filtrado.iterrows():
#         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#             latitude, longitude = row['Latitude'], row['Longitude']
#             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
#             marker = folium.Marker(location=[latitude, longitude],
#                                    popup=folium.Popup(popup_content, max_width=300)
#                                    ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])
#
#             tempo_anterior = row['DataHora']
#
#     folium.LayerControl().add_to(mapa)
#
#     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#     mapa.save(caminho_mapa)
#
#     return caminho_mapa
#
#
# from flask import send_from_directory
#
#
# @app.route('/mapa_gerado/<filename>')
# def mapa_gerado(filename):
#     return send_from_directory('static', filename)
#
#
# @app.route('/mapa_deslocamento')
# def mapa_deslocamento():
#     return render_template('mapa_deslocamento.html')
#
#
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))
#
#     global df
#
#     mapa_gerado = False
#     caminho_mapa = None
#
#     if request.method == 'POST':
#         print("Método POST detectado")
#         print("Dados do formulário:")
#         print(request.form)
#         print("Arquivos enviados:")
#         print(request.files)
#
#         data_inicial = request.form['data_inicial']
#         hora_inicial = request.form['hora_inicial']
#         data_final = request.form['data_final']
#         hora_final = request.form['hora_final']
#
#         if not all([data_inicial, hora_inicial, data_final, hora_final]):
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Forneça todas datas e horas")
#
#         if 'arquivo_csv' not in request.files:
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         file = request.files['arquivo_csv']
#
#         if file.filename == '':
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             os.makedirs('static', exist_ok=True)
#
#             # MODIFICAÇÃO 4: Usar a função unificada de carregamento
#             df = carregar_dataframe(file_path)
#
#             if df.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro="Erro ao carregar o arquivo. Verifique o formato e as colunas necessárias.")
#
#             filtro = ((df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}', format='%Y-%m-%d %H:%M:%S')) &
#                       (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}', format='%Y-%m-%d %H:%M:%S')))
#             df_filtrado = df[filtro].copy()
#             print(df_filtrado)
#
#             if df_filtrado.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro=f"Não há dados no intervalo de datas especificado: {data_inicial} {hora_inicial} - {data_final} {hora_final}")
#
#             caminho_mapa = criar_mapa(df_filtrado)
#             mapa_gerado = True
#         else:
#             return render_template('index.html', mapa_gerado=False,
#                                    mensagem_erro="Formato de arquivo não permitido. Use apenas CSV ou XLSX.")
#
#     if mapa_gerado:
#         link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
#     else:
#         link_download = None
#
#     return render_template('index.html', mapa_gerado=mapa_gerado, caminho_mapa=caminho_mapa,
#                            link_download=link_download)
#
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('login'))
#
#
# def abrir_mapa_no_navegador():
#     sistema_operacional = platform.system()
#     caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')
#
#     if sistema_operacional == 'Windows':
#         os.startfile(caminho_arquivo_html)
#     elif sistema_operacional == 'Linux':
#         os.system('xdg-open' + caminho_arquivo_html)
#     else:
#         print('Sistema operacional não suportado')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request, redirect, url_for, session
# from folium.plugins import HeatMap
# import pandas as pd
# import folium
# import os
# from werkzeug.utils import secure_filename
# import platform
# import io
# from base64 import b64encode
# import sqlite3
#
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
# app.config['UPLOAD_FOLDER'] = 'uploads'
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         if username == 'admin' and password == 'admin':
#             session['logged_in'] = True
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')
#
#     return render_template('login.html')
#
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# df = pd.DataFrame()
# intervalo_minutos = 3
#
#
# def detectar_tipo_arquivo(df):
#     """
#     Detecta o tipo de estrutura do arquivo baseado nas colunas
#     """
#     colunas = df.columns.tolist()
#     print(f"Colunas detectadas: {colunas}")
#
#     # Formato antigo (CSV): Data, Hora, Latitude, Longitude, Velocidade, Placa
#     if 'Data' in colunas and 'Hora' in colunas:
#         return 'formato_antigo'
#
#     # Formato novo (XLSX): HR Evento, Lat/Long, Velocidade, Placa
#     elif 'HR Evento' in colunas and 'Lat/Long' in colunas:
#         return 'formato_novo'
#
#     # Pode adicionar mais formatos aqui no futuro
#     else:
#         return 'desconhecido'
#
#
# def processar_formato_antigo(df):
#     """
#     Processa arquivos no formato antigo (CSV)
#     """
#     print("Processando formato antigo (CSV)")
#
#     # Verificações do formato antigo
#     if 'Data' not in df.columns or 'Hora' not in df.columns:
#         raise ValueError("O arquivo não contém as colunas 'Data' e 'Hora'.")
#
#     # Crie a coluna 'DataHora'
#     df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S')
#
#     # Converta Latitude e Longitude
#     df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
#     df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)
#
#     return df
#
#
# def processar_formato_novo(df):
#     """
#     Processa arquivos no formato novo (XLSX)
#     """
#     print("Processando formato novo (XLSX)")
#
#     # Verificações do formato novo
#     if 'HR Evento' not in df.columns:
#         raise ValueError("O arquivo não contém a coluna 'HR Evento'.")
#
#     if 'Lat/Long' not in df.columns:
#         raise ValueError("O arquivo não contém a coluna 'Lat/Long'.")
#
#     # Processa a coluna de data/hora
#     # HR Evento já está no formato datetime ou string '21/07/2025 00:16'
#     df['DataHora'] = pd.to_datetime(df['HR Evento'], format='%d/%m/%Y %H:%M', errors='coerce')
#
#     # Se não funcionou, tenta outros formatos
#     if df['DataHora'].isna().all():
#         df['DataHora'] = pd.to_datetime(df['HR Evento'], errors='coerce')
#
#     # Processa Lat/Long (formato: "-25.534512, -49.09264")
#     # Separa latitude e longitude
#     lat_long_split = df['Lat/Long'].str.split(',', expand=True)
#     df['Latitude'] = lat_long_split[0].str.strip().astype(float)
#     df['Longitude'] = lat_long_split[1].str.strip().astype(float)
#
#     # Cria colunas Data e Hora para compatibilidade com o resto do código
#     df['Data'] = df['DataHora'].dt.strftime('%d/%m/%Y')
#     df['Hora'] = df['DataHora'].dt.strftime('%H:%M:%S')
#
#     # Renomeia/ajusta outras colunas se necessário
#     if 'Velocidac' in df.columns:  # caso tenha nome truncado
#         df['Velocidade'] = df['Velocidac']
#     elif 'Velocidade' not in df.columns:
#         df['Velocidade'] = 0  # valor padrão se não existir
#
#     return df
#
#
# def carregar_dataframe_csv(caminho):
#     try:
#         print(f'Tentando carregar o arquivo CSV {caminho}')
#         df = pd.read_csv(caminho, encoding='ISO-8859-1')
#
#         tipo_arquivo = detectar_tipo_arquivo(df)
#         print(f"Tipo de arquivo detectado: {tipo_arquivo}")
#
#         if tipo_arquivo == 'formato_antigo':
#             df = processar_formato_antigo(df)
#         elif tipo_arquivo == 'formato_novo':
#             df = processar_formato_novo(df)
#         else:
#             raise ValueError("Formato de arquivo não reconhecido. Verifique as colunas do arquivo.")
#
#         print("DataFrame CSV carregado com sucesso")
#         print(f"Primeiras linhas:\n{df.head()}")
#         print(f"Colunas finais: {df.columns.tolist()}")
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo CSV: {e}')
#         return pd.DataFrame()
#
#
# def carregar_dataframe_xlsx(caminho):
#     try:
#         print(f'Tentando carregar o arquivo XLSX {caminho}')
#         df = pd.read_excel(caminho, sheet_name=0)
#
#         tipo_arquivo = detectar_tipo_arquivo(df)
#         print(f"Tipo de arquivo detectado: {tipo_arquivo}")
#
#         if tipo_arquivo == 'formato_antigo':
#             df = processar_formato_antigo(df)
#         elif tipo_arquivo == 'formato_novo':
#             df = processar_formato_novo(df)
#         else:
#             raise ValueError("Formato de arquivo não reconhecido. Verifique as colunas do arquivo.")
#
#         print("DataFrame XLSX carregado com sucesso")
#         print(f"Primeiras linhas:\n{df.head()}")
#         print(f"Colunas finais: {df.columns.tolist()}")
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo XLSX: {e}')
#         return pd.DataFrame()
#
#
# def carregar_dataframe(caminho):
#     """
#     Carrega um DataFrame a partir de um arquivo CSV ou XLSX
#     """
#     extensao = caminho.lower().split('.')[-1]
#
#     if extensao == 'csv':
#         return carregar_dataframe_csv(caminho)
#     elif extensao == 'xlsx':
#         return carregar_dataframe_xlsx(caminho)
#     else:
#         raise ValueError(f"Formato de arquivo não suportado: {extensao}")
#
#
# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     if 'DataHora' not in df_filtrado.columns:
#         print("A coluna 'DataHora' não está presente no DataFrame")
#         return None
#
#     # Criando camadas para cada dia
#     layers = {}
#     for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(),
#                               freq='D'):
#         layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
#
#     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
#
#     # Adicionando camadas ao mapa
#     for layer_name, layer in layers.items():
#         layer.add_to(mapa)
#
#         # Adicionando camadas de diferentes estilos do Google Maps
#         folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Maps Hybrid',
#                          name='Google Maps (Hybrid)').add_to(mapa)
#         folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Satellite',
#                          name='Google Maps (Satélite)').add_to(mapa)
#         folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps',
#                          name='Google Maps (Ruas)').add_to(mapa)
#     # # Adicionando camada para o estilo de satélite do Google Maps
#     # folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Hybrid',
#     #                  name='Google Maps (Hybrid)').add_to(mapa)
#
#     # Criando camada para HeatMap
#     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#     HeatMap(dados_heatmap).add_to(mapa)
#
#     # Criando camada separada para a linha de trajeto (PolyLine)
#     trajeto_layer = folium.FeatureGroup(name="Trajeto do Veículo")
#     trajeto_layer.add_to(mapa)
#
#     # Criando a linha vermelha com todos os pontos do trajeto
#     pontos_trajeto = df_filtrado[['Latitude', 'Longitude']].values.tolist()
#     folium.PolyLine(
#         locations=pontos_trajeto,
#         weight=3,
#         color='red',
#         opacity=0.8,
#         popup="Trajeto completo do veículo"
#     ).add_to(trajeto_layer)
#
#     tempo_anterior = None
#
#     # Iterando sobre os dados com intervalo_minutos
#     for _, row in df_filtrado.iterrows():
#         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#             latitude, longitude = row['Latitude'], row['Longitude']
#             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
#             marker = folium.Marker(location=[latitude, longitude],
#                                    popup=folium.Popup(popup_content, max_width=300)
#                                    ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])
#
#             tempo_anterior = row['DataHora']
#
#     # Adicionando controle de camadas ao mapa
#     folium.LayerControl().add_to(mapa)
#
#     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#     mapa.save(caminho_mapa)
#
#     return caminho_mapa
#
#
# from flask import send_from_directory
#
#
# @app.route('/mapa_gerado/<filename>')
# def mapa_gerado(filename):
#     return send_from_directory('static', filename)
#
#
# @app.route('/mapa_deslocamento')
# def mapa_deslocamento():
#     return render_template('mapa_deslocamento.html')
#
#
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))
#
#     global df
#
#     mapa_gerado = False
#     caminho_mapa = None
#
#     if request.method == 'POST':
#         print("Método POST detectado")
#         print("Dados do formulário:")
#         print(request.form)
#         print("Arquivos enviados:")
#         print(request.files)
#
#         data_inicial = request.form['data_inicial']
#         hora_inicial = request.form['hora_inicial']
#         data_final = request.form['data_final']
#         hora_final = request.form['hora_final']
#
#         if not all([data_inicial, hora_inicial, data_final, hora_final]):
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Forneça todas datas e horas")
#
#         if 'arquivo_csv' not in request.files:
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         file = request.files['arquivo_csv']
#
#         if file.filename == '':
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             os.makedirs('static', exist_ok=True)
#
#             # Carregar o arquivo com detecção automática de formato
#             df = carregar_dataframe(file_path)
#
#             if df.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro="Erro ao carregar o arquivo. Verifique o formato e as colunas necessárias.")
#
#             # Verificar se as colunas essenciais existem após o processamento
#             colunas_essenciais = ['DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']
#             colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]
#
#             if colunas_faltando:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro=f"Colunas essenciais não encontradas após processamento: {colunas_faltando}")
#
#             filtro = ((df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}', format='%Y-%m-%d %H:%M:%S')) &
#                       (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}', format='%Y-%m-%d %H:%M:%S')))
#             df_filtrado = df[filtro].copy()
#             print(f"Dados filtrados: {len(df_filtrado)} registros")
#
#             if df_filtrado.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro=f"Não há dados no intervalo de datas especificado: {data_inicial} {hora_inicial} - {data_final} {hora_final}")
#
#             caminho_mapa = criar_mapa(df_filtrado)
#             mapa_gerado = True
#         else:
#             return render_template('index.html', mapa_gerado=False,
#                                    mensagem_erro="Formato de arquivo não permitido. Use apenas CSV ou XLSX.")
#
#     if mapa_gerado:
#         link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
#     else:
#         link_download = None
#
#     return render_template('index.html', mapa_gerado=mapa_gerado, caminho_mapa=caminho_mapa,
#                            link_download=link_download)
#
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('login'))
#
#
# def abrir_mapa_no_navegador():
#     sistema_operacional = platform.system()
#     caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')
#
#     if sistema_operacional == 'Windows':
#         os.startfile(caminho_arquivo_html)
#     elif sistema_operacional == 'Linux':
#         os.system('xdg-open' + caminho_arquivo_html)
#     else:
#         print('Sistema operacional não suportado')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, render_template, request, redirect, url_for, session
# from folium.plugins import HeatMap
# import pandas as pd
# import folium
# import os
# from werkzeug.utils import secure_filename
# import platform
# import io
# from base64 import b64encode
# import sqlite3
#
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
#
# app = Flask(__name__)
#
# app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
# app.config['UPLOAD_FOLDER'] = 'uploads'
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#
#         if username == 'admin' and password == 'admin':
#             session['logged_in'] = True
#             return redirect(url_for('index'))
#         else:
#             return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')
#
#     return render_template('login.html')
#
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# df = pd.DataFrame()
# intervalo_minutos = 3
#
#
# def detectar_tipo_arquivo(df):
#     """
#     Detecta o tipo de estrutura do arquivo baseado nas colunas
#     """
#     colunas = df.columns.tolist()
#     print(f"Colunas detectadas: {colunas}")
#
#     # Formato antigo (CSV): Data, Hora, Latitude, Longitude, Velocidade, Placa
#     if 'Data' in colunas and 'Hora' in colunas:
#         return 'formato_antigo'
#
#     # Formato novo (XLSX): HR Evento, Lat/Long, Velocidade, Placa
#     elif 'HR Evento' in colunas and 'Lat/Long' in colunas:
#         return 'formato_novo'
#
#     # Pode adicionar mais formatos aqui no futuro
#     else:
#         return 'desconhecido'
#
#
# def processar_formato_antigo(df):
#     """
#     Processa arquivos no formato antigo (CSV e XLSX)
#     """
#     print("Processando formato antigo")
#
#     # Verificações do formato antigo
#     if 'Data' not in df.columns or 'Hora' not in df.columns:
#         raise ValueError("O arquivo não contém as colunas 'Data' e 'Hora'.")
#
#     # Converter 'Data' para string se necessário
#     df['Data'] = df['Data'].astype(str)
#
#     # Tratar a coluna 'Hora' que pode vir como datetime.time, datetime.datetime ou string
#     def converter_hora(hora_value):
#         if pd.isna(hora_value):
#             return "00:00:00"
#
#         # Se for datetime.time
#         if hasattr(hora_value, 'strftime') and hasattr(hora_value, 'hour'):
#             if hasattr(hora_value, 'date'):  # datetime.datetime
#                 return hora_value.strftime('%H:%M:%S')
#             else:  # datetime.time
#                 return hora_value.strftime('%H:%M:%S')
#
#         # Se for string, retorna como está
#         if isinstance(hora_value, str):
#             return hora_value
#
#         # Caso contrário, tenta converter para string
#         return str(hora_value)
#
#     df['Hora'] = df['Hora'].apply(converter_hora)
#
#     # Criar a coluna 'DataHora'
#     try:
#         # Primeiro tenta o formato padrão
#         df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
#
#         # Se muitos valores ficaram NaT, tenta outros formatos
#         if df['DataHora'].isna().sum() > len(df) * 0.5:  # Se mais de 50% falharam
#             df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], errors='coerce')
#     except Exception as e:
#         print(f"Erro ao criar DataHora: {e}")
#         # Última tentativa com conversão automática
#         df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], errors='coerce')
#
#     # Verificar se a conversão funcionou
#     if df['DataHora'].isna().all():
#         raise ValueError("Não foi possível converter as colunas Data e Hora em DataHora.")
#
#     # Converter Latitude e Longitude
#     # Para arquivos XLSX, pode já estar como float ou string
#     def converter_coordenada(coord_value):
#         if pd.isna(coord_value):
#             return 0.0
#
#         if isinstance(coord_value, (int, float)):
#             return float(coord_value)
#
#         # Se for string, trata vírgula como separador decimal
#         if isinstance(coord_value, str):
#             return float(coord_value.replace(',', '.'))
#
#         return float(coord_value)
#
#     df['Latitude'] = df['Latitude'].apply(converter_coordenada)
#     df['Longitude'] = df['Longitude'].apply(converter_coordenada)
#
#     return df
#
#
# def processar_formato_novo(df):
#     """
#     Processa arquivos no formato novo (XLSX)
#     """
#     print("Processando formato novo (XLSX)")
#
#     # Verificações do formato novo
#     if 'HR Evento' not in df.columns:
#         raise ValueError("O arquivo não contém a coluna 'HR Evento'.")
#
#     if 'Lat/Long' not in df.columns:
#         raise ValueError("O arquivo não contém a coluna 'Lat/Long'.")
#
#     # Processa a coluna de data/hora
#     # HR Evento já está no formato datetime ou string '21/07/2025 00:16'
#     df['DataHora'] = pd.to_datetime(df['HR Evento'], format='%d/%m/%Y %H:%M', errors='coerce')
#
#     # Se não funcionou, tenta outros formatos
#     if df['DataHora'].isna().all():
#         df['DataHora'] = pd.to_datetime(df['HR Evento'], errors='coerce')
#
#     # Processa Lat/Long (formato: "-25.534512, -49.09264")
#     # Separa latitude e longitude
#     lat_long_split = df['Lat/Long'].str.split(',', expand=True)
#     df['Latitude'] = lat_long_split[0].str.strip().astype(float)
#     df['Longitude'] = lat_long_split[1].str.strip().astype(float)
#
#     # Cria colunas Data e Hora para compatibilidade com o resto do código
#     df['Data'] = df['DataHora'].dt.strftime('%d/%m/%Y')
#     df['Hora'] = df['DataHora'].dt.strftime('%H:%M:%S')
#
#     # Renomeia/ajusta outras colunas se necessário
#     if 'Velocidac' in df.columns:  # caso tenha nome truncado
#         df['Velocidade'] = df['Velocidac']
#     elif 'Velocidade' not in df.columns:
#         df['Velocidade'] = 0  # valor padrão se não existir
#
#     return df
#
#
# def carregar_dataframe_csv(caminho):
#     try:
#         print(f'Tentando carregar o arquivo CSV {caminho}')
#         df = pd.read_csv(caminho, encoding='ISO-8859-1')
#
#         tipo_arquivo = detectar_tipo_arquivo(df)
#         print(f"Tipo de arquivo detectado: {tipo_arquivo}")
#
#         if tipo_arquivo == 'formato_antigo':
#             df = processar_formato_antigo(df)
#         elif tipo_arquivo == 'formato_novo':
#             df = processar_formato_novo(df)
#         else:
#             raise ValueError("Formato de arquivo não reconhecido. Verifique as colunas do arquivo.")
#
#         print("DataFrame CSV carregado com sucesso")
#         print(f"Primeiras linhas:\n{df.head()}")
#         print(f"Colunas finais: {df.columns.tolist()}")
#
#         return df
#     except Exception as e:
#         print(f'Erro ao carregar arquivo CSV: {e}')
#         return pd.DataFrame()
#
#
# def carregar_dataframe_xlsx(caminho):
#     try:
#         print(f'Tentando carregar o arquivo XLSX {caminho}')
#         df = pd.read_excel(caminho, sheet_name=0)
#
#         print(f"Arquivo XLSX carregado. Shape: {df.shape}")
#         print(f"Colunas: {df.columns.tolist()}")
#         print(f"Primeiras linhas:\n{df.head(2)}")
#
#         # Verificar tipos de dados das colunas principais
#         if 'Hora' in df.columns:
#             print(f"Tipo da coluna 'Hora': {df['Hora'].dtype}")
#             print(f"Exemplo de valores da coluna 'Hora': {df['Hora'].head(3).tolist()}")
#
#         tipo_arquivo = detectar_tipo_arquivo(df)
#         print(f"Tipo de arquivo detectado: {tipo_arquivo}")
#
#         if tipo_arquivo == 'formato_antigo':
#             df = processar_formato_antigo(df)
#         elif tipo_arquivo == 'formato_novo':
#             df = processar_formato_novo(df)
#         else:
#             raise ValueError(f"Formato de arquivo não reconhecido. Colunas encontradas: {df.columns.tolist()}")
#
#         print("DataFrame XLSX processado com sucesso")
#         print(f"Colunas após processamento: {df.columns.tolist()}")
#         print(
#             f"Amostra dos dados processados:\n{df[['Data', 'Hora', 'DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']].head(3)}")
#
#         return df
#     except Exception as e:
#         print(f'Erro detalhado ao carregar arquivo XLSX: {e}')
#         print(f'Tipo do erro: {type(e).__name__}')
#         import traceback
#         traceback.print_exc()
#         return pd.DataFrame()
#
#
# def carregar_dataframe(caminho):
#     """
#     Carrega um DataFrame a partir de um arquivo CSV ou XLSX
#     """
#     extensao = caminho.lower().split('.')[-1]
#
#     if extensao == 'csv':
#         return carregar_dataframe_csv(caminho)
#     elif extensao == 'xlsx':
#         return carregar_dataframe_xlsx(caminho)
#     else:
#         raise ValueError(f"Formato de arquivo não suportado: {extensao}")
#
#
# def criar_mapa(df_filtrado, intervalo_minutos=3):
#     if 'DataHora' not in df_filtrado.columns:
#         print("A coluna 'DataHora' não está presente no DataFrame")
#         return None
#
#     # Criando camadas para cada dia
#     layers = {}
#     for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(),
#                               freq='D'):
#         layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))
#
#     mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)
#
#     # Adicionando camadas ao mapa
#     for layer_name, layer in layers.items():
#         layer.add_to(mapa)
#
#     # Adicionando camadas de diferentes estilos do Google Maps
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Maps Hybrid',
#                      name='Google Maps (Hybrid)').add_to(mapa)
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Satellite',
#                      name='Google Maps (Satélite)').add_to(mapa)
#     folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps',
#                      name='Google Maps (Ruas)').add_to(mapa)
#
#     # Criando camada para HeatMap
#     df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
#     dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
#     HeatMap(dados_heatmap).add_to(mapa)
#
#     # Criando camada separada para a linha de trajeto (PolyLine)
#     trajeto_layer = folium.FeatureGroup(name="Trajeto do Veículo")
#     trajeto_layer.add_to(mapa)
#
#     # Criando a linha vermelha com todos os pontos do trajeto
#     pontos_trajeto = df_filtrado[['Latitude', 'Longitude']].values.tolist()
#     folium.PolyLine(
#         locations=pontos_trajeto,
#         weight=3,
#         color='red',
#         opacity=0.8,
#         popup="Trajeto completo do veículo"
#     ).add_to(trajeto_layer)
#
#     tempo_anterior = None
#
#     # Iterando sobre os dados com intervalo_minutos para os marcadores
#     for _, row in df_filtrado.iterrows():
#         if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
#             latitude, longitude = row['Latitude'], row['Longitude']
#             google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
#             popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"
#
#             marker = folium.Marker(location=[latitude, longitude],
#                                    popup=folium.Popup(popup_content, max_width=300)
#                                    ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])
#
#             tempo_anterior = row['DataHora']
#
#     # Adicionando controle de camadas ao mapa
#     folium.LayerControl().add_to(mapa)
#
#     caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
#     mapa.save(caminho_mapa)
#
#     return caminho_mapa
#
#
# from flask import send_from_directory
#
#
# @app.route('/mapa_gerado/<filename>')
# def mapa_gerado(filename):
#     return send_from_directory('static', filename)
#
#
# @app.route('/mapa_deslocamento')
# def mapa_deslocamento():
#     return render_template('mapa_deslocamento.html')
#
#
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if 'logged_in' not in session or not session['logged_in']:
#         return redirect(url_for('login'))
#
#     global df
#
#     mapa_gerado = False
#     caminho_mapa = None
#
#     if request.method == 'POST':
#         print("Método POST detectado")
#         print("Dados do formulário:")
#         print(request.form)
#         print("Arquivos enviados:")
#         print(request.files)
#
#         data_inicial = request.form['data_inicial']
#         hora_inicial = request.form['hora_inicial']
#         data_final = request.form['data_final']
#         hora_final = request.form['hora_final']
#
#         if not all([data_inicial, hora_inicial, data_final, hora_final]):
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Forneça todas datas e horas")
#
#         if 'arquivo_csv' not in request.files:
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         file = request.files['arquivo_csv']
#
#         if file.filename == '':
#             return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")
#
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             os.makedirs('static', exist_ok=True)
#
#             # Carregar o arquivo com detecção automática de formato
#             df = carregar_dataframe(file_path)
#
#             if df.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro="Erro ao carregar o arquivo. Verifique o formato e as colunas necessárias.")
#
#             # Verificar se as colunas essenciais existem após o processamento
#             colunas_essenciais = ['DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']
#             colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]
#
#             if colunas_faltando:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro=f"Colunas essenciais não encontradas após processamento: {colunas_faltando}")
#
#             filtro = ((df['DataHora'] >= pd.to_datetime(f'{data_inicial} {hora_inicial}', format='%Y-%m-%d %H:%M:%S')) &
#                       (df['DataHora'] <= pd.to_datetime(f'{data_final} {hora_final}', format='%Y-%m-%d %H:%M:%S')))
#             df_filtrado = df[filtro].copy()
#             print(f"Dados filtrados: {len(df_filtrado)} registros")
#
#             if df_filtrado.empty:
#                 return render_template('index.html', mapa_gerado=False,
#                                        mensagem_erro=f"Não há dados no intervalo de datas especificado: {data_inicial} {hora_inicial} - {data_final} {hora_final}")
#
#             caminho_mapa = criar_mapa(df_filtrado)
#             mapa_gerado = True
#         else:
#             return render_template('index.html', mapa_gerado=False,
#                                    mensagem_erro="Formato de arquivo não permitido. Use apenas CSV ou XLSX.")
#
#     if mapa_gerado:
#         link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
#     else:
#         link_download = None
#
#     return render_template('index.html', mapa_gerado=mapa_gerado, caminho_mapa=caminho_mapa,
#                            link_download=link_download)
#
#
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     return redirect(url_for('login'))
#
#
# def abrir_mapa_no_navegador():
#     sistema_operacional = platform.system()
#     caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')
#
#     if sistema_operacional == 'Windows':
#         os.startfile(caminho_arquivo_html)
#     elif sistema_operacional == 'Linux':
#         os.system('xdg-open' + caminho_arquivo_html)
#     else:
#         print('Sistema operacional não suportado')
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

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
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app = Flask(__name__)

app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', mensagem_erro='Credenciais inválidas. Tente novamente.')

    return render_template('login.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


df = pd.DataFrame()
intervalo_minutos = 3


def detectar_tipo_arquivo(df):
    """
    Detecta o tipo de estrutura do arquivo baseado nas colunas
    """
    colunas = df.columns.tolist()
    print(f"Colunas detectadas: {colunas}")

    # Formato antigo (CSV): Data, Hora, Latitude, Longitude, Velocidade, Placa
    if 'Data' in colunas and 'Hora' in colunas:
        return 'formato_antigo'

    # Formato novo (XLSX): HR Evento, Lat/Long, Velocidade, Placa
    elif 'HR Evento' in colunas and 'Lat/Long' in colunas:
        return 'formato_novo'

    # Pode adicionar mais formatos aqui no futuro
    else:
        return 'desconhecido'


def processar_formato_antigo(df):
    """
    Processa arquivos no formato antigo (CSV e XLSX)
    """
    print("Processando formato antigo")

    # Verificações do formato antigo
    if 'Data' not in df.columns or 'Hora' not in df.columns:
        raise ValueError("O arquivo não contém as colunas 'Data' e 'Hora'.")

    # Converter 'Data' para string se necessário
    df['Data'] = df['Data'].astype(str)

    # Tratar a coluna 'Hora' que pode vir como datetime.time, datetime.datetime ou string
    def converter_hora(hora_value):
        if pd.isna(hora_value):
            return "00:00:00"

        # Se for datetime.time
        if hasattr(hora_value, 'strftime') and hasattr(hora_value, 'hour'):
            if hasattr(hora_value, 'date'):  # datetime.datetime
                return hora_value.strftime('%H:%M:%S')
            else:  # datetime.time
                return hora_value.strftime('%H:%M:%S')

        # Se for string, retorna como está
        if isinstance(hora_value, str):
            return hora_value

        # Caso contrário, tenta converter para string
        return str(hora_value)

    df['Hora'] = df['Hora'].apply(converter_hora)

    # Criar a coluna 'DataHora'
    try:
        # Primeiro tenta o formato padrão
        df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], format='%d/%m/%Y %H:%M:%S', errors='coerce')

        # Se muitos valores ficaram NaT, tenta outros formatos
        if df['DataHora'].isna().sum() > len(df) * 0.5:  # Se mais de 50% falharam
            df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], errors='coerce')
    except Exception as e:
        print(f"Erro ao criar DataHora: {e}")
        # Última tentativa com conversão automática
        df['DataHora'] = pd.to_datetime(df['Data'] + ' ' + df['Hora'], errors='coerce')

    # Verificar se a conversão funcionou
    if df['DataHora'].isna().all():
        raise ValueError("Não foi possível converter as colunas Data e Hora em DataHora.")

    # Converter Latitude e Longitude
    # Para arquivos XLSX, pode já estar como float ou string
    def converter_coordenada(coord_value):
        if pd.isna(coord_value):
            return 0.0

        if isinstance(coord_value, (int, float)):
            return float(coord_value)

        # Se for string, trata vírgula como separador decimal
        if isinstance(coord_value, str):
            return float(coord_value.replace(',', '.'))

        return float(coord_value)

    df['Latitude'] = df['Latitude'].apply(converter_coordenada)
    df['Longitude'] = df['Longitude'].apply(converter_coordenada)

    return df


def processar_formato_novo(df):
    """
    Processa arquivos no formato novo (XLSX)
    """
    print("Processando formato novo (XLSX)")

    # Verificações do formato novo
    if 'HR Evento' not in df.columns:
        raise ValueError("O arquivo não contém a coluna 'HR Evento'.")

    if 'Lat/Long' not in df.columns:
        raise ValueError("O arquivo não contém a coluna 'Lat/Long'.")

    # Processa a coluna de data/hora
    # HR Evento já está no formato datetime ou string '21/07/2025 00:16'
    df['DataHora'] = pd.to_datetime(df['HR Evento'], format='%d/%m/%Y %H:%M', errors='coerce')

    # Se não funcionou, tenta outros formatos
    if df['DataHora'].isna().all():
        df['DataHora'] = pd.to_datetime(df['HR Evento'], errors='coerce')

    # Processa Lat/Long (formato: "-25.534512, -49.09264")
    # Separa latitude e longitude
    lat_long_split = df['Lat/Long'].str.split(',', expand=True)
    df['Latitude'] = lat_long_split[0].str.strip().astype(float)
    df['Longitude'] = lat_long_split[1].str.strip().astype(float)

    # Cria colunas Data e Hora para compatibilidade com o resto do código
    df['Data'] = df['DataHora'].dt.strftime('%d/%m/%Y')
    df['Hora'] = df['DataHora'].dt.strftime('%H:%M:%S')

    # Renomeia/ajusta outras colunas se necessário
    if 'Velocidac' in df.columns:  # caso tenha nome truncado
        df['Velocidade'] = df['Velocidac']
    elif 'Velocidade' not in df.columns:
        df['Velocidade'] = 0  # valor padrão se não existir

    return df


def carregar_dataframe_csv(caminho):
    try:
        print(f'Tentando carregar o arquivo CSV {caminho}')
        df = pd.read_csv(caminho, encoding='ISO-8859-1')

        tipo_arquivo = detectar_tipo_arquivo(df)
        print(f"Tipo de arquivo detectado: {tipo_arquivo}")

        if tipo_arquivo == 'formato_antigo':
            df = processar_formato_antigo(df)
        elif tipo_arquivo == 'formato_novo':
            df = processar_formato_novo(df)
        else:
            raise ValueError("Formato de arquivo não reconhecido. Verifique as colunas do arquivo.")

        print("DataFrame CSV carregado com sucesso")
        print(f"Primeiras linhas:\n{df.head()}")
        print(f"Colunas finais: {df.columns.tolist()}")

        return df
    except Exception as e:
        print(f'Erro ao carregar arquivo CSV: {e}')
        return pd.DataFrame()


def carregar_dataframe_xlsx(caminho):
    try:
        print(f'Tentando carregar o arquivo XLSX {caminho}')
        df = pd.read_excel(caminho, sheet_name=0)

        print(f"Arquivo XLSX carregado. Shape: {df.shape}")
        print(f"Colunas: {df.columns.tolist()}")
        print(f"Primeiras linhas:\n{df.head(2)}")

        # Verificar tipos de dados das colunas principais
        if 'Hora' in df.columns:
            print(f"Tipo da coluna 'Hora': {df['Hora'].dtype}")
            print(f"Exemplo de valores da coluna 'Hora': {df['Hora'].head(3).tolist()}")

        tipo_arquivo = detectar_tipo_arquivo(df)
        print(f"Tipo de arquivo detectado: {tipo_arquivo}")

        if tipo_arquivo == 'formato_antigo':
            df = processar_formato_antigo(df)
        elif tipo_arquivo == 'formato_novo':
            df = processar_formato_novo(df)
        else:
            raise ValueError(f"Formato de arquivo não reconhecido. Colunas encontradas: {df.columns.tolist()}")

        print("DataFrame XLSX processado com sucesso")
        print(f"Colunas após processamento: {df.columns.tolist()}")
        print(
            f"Amostra dos dados processados:\n{df[['Data', 'Hora', 'DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']].head(3)}")

        return df
    except Exception as e:
        print(f'Erro detalhado ao carregar arquivo XLSX: {e}')
        print(f'Tipo do erro: {type(e).__name__}')
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def carregar_dataframe(caminho):
    """
    Carrega um DataFrame a partir de um arquivo CSV ou XLSX
    """
    extensao = caminho.lower().split('.')[-1]

    if extensao == 'csv':
        return carregar_dataframe_csv(caminho)
    elif extensao == 'xlsx':
        return carregar_dataframe_xlsx(caminho)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {extensao}")


def criar_mapa(df_filtrado, intervalo_minutos=3):
    if 'DataHora' not in df_filtrado.columns:
        print("A coluna 'DataHora' não está presente no DataFrame")
        return None

    # Criando camadas para cada dia
    layers = {}
    for data in pd.date_range(start=df_filtrado['DataHora'].min().date(), end=df_filtrado['DataHora'].max().date(),
                              freq='D'):
        layers[data.strftime('%d/%m/%Y')] = folium.FeatureGroup(name=data.strftime('%d/%m/%Y'))

    mapa = folium.Map(location=[df_filtrado.iloc[0]['Latitude'], df_filtrado.iloc[0]['Longitude']], zoom_start=14)

    # Adicionando camadas ao mapa
    for layer_name, layer in layers.items():
        layer.add_to(mapa)

    # Adicionando camadas de diferentes estilos do Google Maps
    folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Maps Hybrid',
                     name='Google Maps (Hybrid)').add_to(mapa)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google Maps Satellite',
                     name='Google Maps (Satélite)').add_to(mapa)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', attr='Google Maps',
                     name='Google Maps (Ruas)').add_to(mapa)

    # Criando camada para HeatMap
    df_velocidade_zero = df_filtrado[df_filtrado['Velocidade'] == 0]
    dados_heatmap = df_velocidade_zero[['Latitude', 'Longitude']].values.tolist()
    HeatMap(dados_heatmap).add_to(mapa)

    # Criando camada separada para a linha de trajeto (PolyLine)
    trajeto_layer = folium.FeatureGroup(name="Trajeto do Veículo")
    trajeto_layer.add_to(mapa)

    # Criando a linha vermelha com todos os pontos do trajeto
    pontos_trajeto = df_filtrado[['Latitude', 'Longitude']].values.tolist()
    folium.PolyLine(
        locations=pontos_trajeto,
        weight=3,
        color='red',
        opacity=0.8,
        popup="Trajeto completo do veículo"
    ).add_to(trajeto_layer)

    tempo_anterior = None

    # Iterando sobre os dados com intervalo_minutos para os marcadores
    for _, row in df_filtrado.iterrows():
        if tempo_anterior is None or (row['DataHora'] - tempo_anterior).seconds >= intervalo_minutos * 60:
            latitude, longitude = row['Latitude'], row['Longitude']
            google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
            popup_content = f"{row['Placa']} - {row['Data']} {row['Hora']} - Velocidade: {row['Velocidade']} km/h - LatLong: {[latitude, longitude]}<br><a href='{google_maps_link}' target='_blank'>Ver no Google Maps</a>"

            marker = folium.Marker(location=[latitude, longitude],
                                   popup=folium.Popup(popup_content, max_width=300)
                                   ).add_to(layers[row['DataHora'].date().strftime('%d/%m/%Y')])

            tempo_anterior = row['DataHora']

    # Adicionando controle de camadas ao mapa
    folium.LayerControl().add_to(mapa)

    caminho_mapa = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'mapa_deslocamento.html')
    mapa.save(caminho_mapa)

    return caminho_mapa


from flask import send_from_directory


@app.route('/mapa_gerado/<filename>')
def mapa_gerado(filename):
    return send_from_directory('static', filename)


@app.route('/mapa_deslocamento')
def mapa_deslocamento():
    return render_template('mapa_deslocamento.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    global df

    mapa_gerado = False
    caminho_mapa = None
    info_periodo = None

    if request.method == 'POST':
        print("Método POST detectado")
        print("Dados do formulário:")
        print(request.form)
        print("Arquivos enviados:")
        print(request.files)

        if 'arquivo_csv' not in request.files:
            return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")

        file = request.files['arquivo_csv']

        if file.filename == '':
            return render_template('index.html', mapa_gerado=False, mensagem_erro="Nenhum arquivo enviado")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            os.makedirs('static', exist_ok=True)

            # Carregar o arquivo com detecção automática de formato
            df = carregar_dataframe(file_path)

            if df.empty:
                return render_template('index.html', mapa_gerado=False,
                                       mensagem_erro="Erro ao carregar o arquivo. Verifique o formato e as colunas necessárias.")

            # Verificar se as colunas essenciais existem após o processamento
            colunas_essenciais = ['DataHora', 'Latitude', 'Longitude', 'Velocidade', 'Placa']
            colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]

            if colunas_faltando:
                return render_template('index.html', mapa_gerado=False,
                                       mensagem_erro=f"Colunas essenciais não encontradas após processamento: {colunas_faltando}")

            # NOVA FUNCIONALIDADE: Detectar automaticamente o período dos dados
            data_inicial = df['DataHora'].min()
            data_final = df['DataHora'].max()

            print(f"Período detectado automaticamente:")
            print(f"Data inicial: {data_inicial}")
            print(f"Data final: {data_final}")

            # Criar informações do período para mostrar ao usuário
            info_periodo = {
                'data_inicial': data_inicial.strftime('%d/%m/%Y'),
                'hora_inicial': data_inicial.strftime('%H:%M:%S'),
                'data_final': data_final.strftime('%d/%m/%Y'),
                'hora_final': data_final.strftime('%H:%M:%S'),
                'total_registros': len(df),
                'total_dias': (data_final.date() - data_inicial.date()).days + 1
            }

            # Usar todo o período dos dados (sem filtro adicional)
            df_filtrado = df.copy()
            print(f"Processando todos os dados: {len(df_filtrado)} registros")

            if df_filtrado.empty:
                return render_template('index.html', mapa_gerado=False,
                                       mensagem_erro="Não há dados válidos no arquivo.")

            caminho_mapa = criar_mapa(df_filtrado)
            mapa_gerado = True
        else:
            return render_template('index.html', mapa_gerado=False,
                                   mensagem_erro="Formato de arquivo não permitido. Use apenas CSV ou XLSX.")

    if mapa_gerado:
        link_download = f"/mapa_gerado/{os.path.basename(caminho_mapa)}"
    else:
        link_download = None

    return render_template('index.html',
                           mapa_gerado=mapa_gerado,
                           caminho_mapa=caminho_mapa,
                           link_download=link_download,
                           info_periodo=info_periodo)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


def abrir_mapa_no_navegador():
    sistema_operacional = platform.system()
    caminho_arquivo_html = os.path.join('static', 'mapa_deslocamento.html')

    if sistema_operacional == 'Windows':
        os.startfile(caminho_arquivo_html)
    elif sistema_operacional == 'Linux':
        os.system('xdg-open' + caminho_arquivo_html)
    else:
        print('Sistema operacional não suportado')


if __name__ == '__main__':
    # app.run(debug=True)
    import os

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)