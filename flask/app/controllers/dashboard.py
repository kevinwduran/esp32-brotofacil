from flask import Blueprint, render_template
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
import plotly.io as pio
from models.sensor_data import DadosSensor
from flask_login import login_required
from decorators.role_required import role_required

# Criação do Blueprint para o dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Rota para visualizar o dashboard (somente admin)
@dashboard_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Definir a quantidade de dias a serem filtrados
    DIAS_DE_FILTRAGEM = 7
    data_limite = datetime.now(ZoneInfo('America/Sao_Paulo')) - timedelta(days=DIAS_DE_FILTRAGEM)

    # Buscar dados do banco nos últimos DIAS_DE_FILTRAGEM dias
    dados = DadosSensor.query.filter(DadosSensor.timestamp >= data_limite).order_by(DadosSensor.timestamp.asc()).all()

    # Preparar dados para os gráficos
    timestamps = [d.timestamp.strftime('%d/%m/%Y %H:%M:%S') for d in dados]
    temperaturas = [d.temperatura for d in dados]
    umidades = [d.umidade for d in dados]
    luminosidades = [d.luminosidade for d in dados]
    umidadesolos = [d.umidadesolo for d in dados]

    # Gráfico de Temperatura
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=timestamps, y=temperaturas, mode='lines+markers', name='Temperatura (°C)', line=dict(color='#66A404')))
    temp_fig.update_layout(title='Temperatura nos Últimos 7 Dias', xaxis_title='Data e Hora', yaxis_title='Temperatura (°C)')
    temp_graph = pio.to_html(temp_fig, full_html=False)

    # Gráfico de Umidade
    umid_fig = go.Figure()
    umid_fig.add_trace(go.Scatter(x=timestamps, y=umidades, mode='lines+markers', name='Umidade (%)', line=dict(color='#1f77b4')))
    umid_fig.update_layout(title='Umidade nos Últimos 7 Dias', xaxis_title='Data e Hora', yaxis_title='Umidade (%)')
    umid_graph = pio.to_html(umid_fig, full_html=False)

    # Gráfico de Luminosidade
    lumi_fig = go.Figure()
    lumi_fig.add_trace(go.Scatter(x=timestamps, y=luminosidades, mode='lines+markers', name='Luminosidade (%)', line=dict(color='#FF5733')))
    lumi_fig.update_layout(title='Luminosidade nos Últimos 7 Dias', xaxis_title='Data e Hora', yaxis_title='Luminosidade (%)')
    lumi_graph = pio.to_html(lumi_fig, full_html=False)

    # Gráfico de Umidade do Solo
    solo_fig = go.Figure()
    solo_fig.add_trace(go.Scatter(x=timestamps, y=umidadesolos, mode='lines+markers', name='Umidade do Solo (%)', line=dict(color='#8B4513')))
    solo_fig.update_layout(title='Umidade do Solo nos Últimos 7 Dias', xaxis_title='Data e Hora', yaxis_title='Umidade do Solo (%)')
    solo_graph = pio.to_html(solo_fig, full_html=False)

    # Renderizar o template com todos os gráficos separados
    return render_template('dashboard.html', temp_graph=temp_graph, umid_graph=umid_graph, lumi_graph=lumi_graph, solo_graph=solo_graph)
