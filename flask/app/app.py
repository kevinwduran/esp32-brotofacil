# Bibliotecas

from flask import Flask,render_template,request,jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
import plotly.io as pio
import csv
from flask import Response
from io import StringIO

# Configurações

app = Flask(__name__, template_folder='templates',
static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.db'
db = SQLAlchemy(app)

app.secret_key = 'sua_chave_secreta_aqui' 


# Função para obter o timespam atual de brasilia

def obter_timestamp_brasilia():
    return datetime.now(ZoneInfo('America/Sao_Paulo'))

# Modelo do banco de dados

class DadosSensor(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    temperatura = db.Column(db.Float, nullable = False)
    umidade = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.DateTime, default = obter_timestamp_brasilia, nullable = False)

# Rota inicial 
@app.route('/')
def index():
    return render_template('index.html')

# Definindo credenciais de exemplo (para fins de teste)
USUARIO_VALIDO = 'admin'
SENHA_VALIDO = 'senha123'  # Altere para uma senha mais segura em produção

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        
        if usuario == USUARIO_VALIDO and senha == SENHA_VALIDO:
            session['usuario_autenticado'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Credenciais inválidas')

    return render_template('login.html')



@app.route('/logout')
def logout():
    session.pop('usuario_autenticado', None)
    return redirect(url_for('index'))

# Rota para visualizar o dashboard
@app.route('/dashboard')
def dashboard():
    if 'usuario_autenticado' not in session:
        return redirect(url_for('login'))
    # Definir a quantidade de dias que deseja filtrar
    DIAS_DE_FILTRAGEM = 7

    # Calcular a data de `DIAS_DE_FILTRAGEM` dias atrás
    data_limite = datetime.now(ZoneInfo('America/Sao_Paulo')) - timedelta(days=DIAS_DE_FILTRAGEM)

    # Consultar os dados do banco filtrando apenas os últimos `DIAS_DE_FILTRAGEM` dias
    dados = DadosSensor.query.filter(DadosSensor.timestamp >= data_limite).order_by(DadosSensor.timestamp.asc()).all()

    # Preparando os dados para os gráficos
    timestamps = [d.timestamp.strftime('%d/%m/%Y %H:%M:%S') for d in dados]
    temperaturas = [d.temperatura for d in dados]
    umidades = [d.umidade for d in dados]

    # Gráfico combinado de Temperatura e Umidade
    fig = go.Figure()

    # Linha de Temperatura
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=temperaturas, 
        mode='lines+markers', 
        name='Temperatura (°C)', 
        line=dict(color='#66A404'),
        marker=dict(size=6),
        hovertemplate='Data: %{x}<br>Temperatura: %{y}°C<extra></extra>'
    ))

    # Linha de Umidade
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=umidades, 
        mode='lines+markers', 
        name='Umidade (%)', 
        line=dict(color='#FFD759'),
        marker=dict(size=6),
        hovertemplate='Data: %{x}<br>Umidade: %{y}%<extra></extra>'
    ))

    # Layout do gráfico
    fig.update_layout(
        title_text='Temperatura e Umidade nos Últimos 7 Dias',
        xaxis_title='Data e Hora',
        yaxis_title='Medições',
        legend=dict(
            x=1,  
            y=0.5,  
            font=dict(size=10),
            bgcolor="rgba(255, 255, 255, 0.5)"
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickangle=-45,  
            zeroline=False,
            nticks=10  
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        margin=dict(l=30, r=100, t=30, b=30),  
        hovermode="x"
    )

    # Converter o gráfico para HTML
    combined_graph = pio.to_html(fig, full_html=False)

    # Renderizar o template com o gráfico
    return render_template('dashboard.html', combined_graph=combined_graph)


# Rota para receber os dados
@app.route('/api/enviar_dados', methods = ['POST'])
def receberDados():
    dados = request.json
    temperatura = dados.get('temperatura')
    umidade = dados.get('umidade')

    if temperatura is None or umidade is None:
        return jsonify({"status":"erro","mensagem":"Dados de temperatura ou umidade ausentes"}), 400
    
    novo_dado = DadosSensor(temperatura = temperatura, umidade = umidade)
    db.session.add(novo_dado)
    db.session.commit()

    return jsonify({"status":"sucesso", "dados_recebidos":dados}), 200



# Rota para exportar dados para CSV
@app.route('/exportar_csv')
def exportar_csv():
    # Consultar todos os dados do banco de dados
    dados = DadosSensor.query.order_by(DadosSensor.timestamp.asc()).all()

    # Verifica se existem dados no banco de dados
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado disponível para exportação"}), 404

    # Nome das colunas no CSV
    colunas = ['ID', 'Temperatura (°C)', 'Umidade (%)', 'Timestamp']

    # Criar um arquivo CSV em memória
    csv_buffer = StringIO()
    escritor_csv = csv.writer(csv_buffer)
    escritor_csv.writerow(colunas)

    # Preencher o CSV com os dados do banco
    for dado in dados:
        escritor_csv.writerow([dado.id, dado.temperatura, dado.umidade, dado.timestamp.strftime('%d/%m/%Y %H:%M:%S')])

    # Definir o conteúdo do CSV como resposta
    resposta_csv = Response(csv_buffer.getvalue(), mimetype='text/csv')
    resposta_csv.headers['Content-Disposition'] = 'attachment; filename=dados_sensores.csv'

    return resposta_csv

# iniciar
if __name__ == '__main__':
    app.secret_key = 'sua_chave_secreta_aqui'
    with app.app_context():
        db.create_all()
    app.run(host = '0.0.0.0', port=5000)