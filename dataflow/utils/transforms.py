import apache_beam as beam
from apache_beam import pvalue
import json
from datetime import datetime

# Função para filtrar dados nulos
def filter_null(event):
    # Se o evento for nulo ou não tiver os campos necessários, descarta
    if event is None or not event.get('type') or not event.get('timestamp'):
        return False
    return True

# Função para processar o evento (compra ou desistência)
def process_event(event):
    event['timestamp'] = datetime.strptime(event['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
    
    # Identificar tipo de evento e direcionar para o arquivo correto
    if event['type'] == 'purchase':
        event['destination'] = 'buy'
    elif event['type'] == 'cancellation':
        event['destination'] = 'cancellation'
    else:
        return None  # Ignorar eventos que não são compra ou desistência
    
    return event

# Função para gravar no GCS com base no tipo de evento
def write_to_gcs(event, path_prefix):
    # Define o caminho do arquivo no GCS, dependendo do evento
    if event:
        path = f"{path_prefix}/{event['destination']}/{event['timestamp'].strftime('%Y/%m/%d/')}"
        return (path, event)
    return None