from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
import plotly.io as pio
from flask_login import current_user
from models.sensor_data import DadosSensor
from flask_login import login_required, current_user
from decorators.role_required import role_required 

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    DIAS_DE_FILTRAGEM = 7
    data_limite = datetime.now(ZoneInfo('America/Sao_Paulo')) - timedelta(days=DIAS_DE_FILTRAGEM)

    # Consultar os dados do banco para os últimos 7 dias
    dados = DadosSensor.query.filter(DadosSensor.timestamp >= data_limite).order_by(DadosSensor.timestamp.asc()).all()

    # Extrair os valores dos dados
    timestamps = [d.timestamp.strftime('%d/%m/%Y %H:%M:%S') for d in dados]
    temperaturas = [d.temperatura for d in dados]
    umidades = [d.umidade for d in dados]
    luminosidades = [d.luminosidade for d in dados] 
    umidadesolos = [d.umidadesolo for d in dados] 

    # Passar os dados para o template
    return render_template(
        'dashboard.html',
        timestamps=timestamps,
        temperaturas=temperaturas,
        umidades=umidades,
        luminosidades=luminosidades,
        umidadesolos=umidadesolos,
        filtro=filtro,  # Enviar o filtro selecionado ao template
        user = current_user
    )
