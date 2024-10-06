from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
import plotly.io as pio
from models.sensor_data import DadosSensor
from models.user import User
from flask_login import login_required
from decorators.role_required import role_required 

dashboard_bp = Blueprint('dashboard', __name__)

# Rota para visualizar o dashboard
# Apenas o usuário admin pode ver
@dashboard_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Definir a quantidade de dias que deseja filtrar
    DIAS_DE_FILTRAGEM = 7
    data_limite = datetime.now(ZoneInfo('America/Sao_Paulo')) - timedelta(days=DIAS_DE_FILTRAGEM)

    # Consultar os dados do banco filtrando apenas os últimos DIAS_DE_FILTRAGEM dias
    dados = DadosSensor.query.filter(DadosSensor.timestamp >= data_limite).order_by(DadosSensor.timestamp.asc()).all()

    # Preparando os dados para os gráficos
    timestamps = [d.timestamp.strftime('%d/%m/%Y %H:%M:%S') for d in dados]
    temperaturas = [d.temperatura for d in dados]
    umidades = [d.umidade for d in dados]
    luminosidades = [d.luminosidade for d in dados] 
    umidadesolos = [d.umidadesolo for d in dados] 

    # Gráfico combinado de Temperatura, Umidade e Luminosidade e umidadesolo
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

    # Linha de Luminosidade
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=luminosidades, 
        mode='lines+markers', 
        name='Luminosidade (%)', 
        line=dict(color='#FF5733'),
        marker=dict(size=6),
        hovertemplate='Data: %{x}<br>Luminosidade: %{y}<extra></extra>'
    ))

    # Linha de Luminosidade
    fig.add_trace(go.Scatter(
        x=timestamps, 
        y=umidadesolos, 
        mode='lines+markers', 
        name='Umidadade do Solo (%)', 
        line=dict(color='#032603'),
        marker=dict(size=6),
        hovertemplate='Data: %{x}<br>Umidadade do Solo: %{y}<extra></extra>'
    ))

    # Layout do gráfico
    fig.update_layout(
        title_text='Dados dos últimos 7 dias',
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