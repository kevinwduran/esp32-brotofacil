from flask import Blueprint, request, jsonify, Response
from models.sensor_data import db, DadosSensor
from io import StringIO
import csv
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/enviar_dados', methods=['POST'])
def receber_dados():
    dados = request.json
    temperatura = dados.get('temperatura')
    umidade = dados.get('umidade')
    luminosidade = dados.get('luminosidade') 
    umidadesolo = dados.get('umidadesolo') 

    if temperatura is None or umidade is None or luminosidade is None or umidadesolo is None:  # Atualize a verificação
        return jsonify({"status": "erro", "mensagem": "Dados de temperatura, umidade, luminosidade ou umidade solo ausentes"}), 400
    
    novo_dado = DadosSensor(temperatura=temperatura, umidade=umidade, luminosidade=luminosidade, umidadesolo=umidadesolo)  # Atualize esta linha
    db.session.add(novo_dado)
    db.session.commit()

    return jsonify({"status": "sucesso", "dados_recebidos": dados}), 200

@api_bp.route('/exportar_csv', methods=['GET'])
def exportar_csv():
    # Consultar todos os dados do banco de dados
    dados = DadosSensor.query.order_by(DadosSensor.timestamp.asc()).all()

    # Verifica se existem dados no banco de dados
    if not dados:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado disponível para exportação"}), 404

    # Nome das colunas no CSV
    colunas = ['ID', 'Temperatura (°C)', 'Umidade (%)', 'Luminosidade (%)', 'Umidade Solo (%)' 'Timestamp']

    # Criar um arquivo CSV em memória
    csv_buffer = StringIO()
    escritor_csv = csv.writer(csv_buffer)
    escritor_csv.writerow(colunas)

    # Preencher o CSV com os dados do banco
    for dado in dados:
        escritor_csv.writerow([dado.id, dado.temperatura, dado.umidade, dado.luminosidade, dado.umidadesolo, dado.timestamp.strftime('%d/%m%Y%H:%M:%S')])

    # Definir o conteúdo do CSV como resposta
    resposta_csv = Response(csv_buffer.getvalue(), mimetype='text/csv')
    resposta_csv.headers['Content-Disposition'] = 'attachment; filename=dados_sensores.csv'

    return resposta_csv