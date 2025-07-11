from app import db
from datetime import datetime
from sqlalchemy import DateTime, String, Float, Integer, Text

class Pesagem(db.Model):
    """Modelo para armazenar os dados de pesagem dos caminhões"""
    id = db.Column(Integer, primary_key=True)
    local_carga = db.Column(String(200), nullable=False)
    local_descarga = db.Column(String(200), nullable=False)
    data = db.Column(DateTime, nullable=False)
    placa_veiculo = db.Column(String(20), nullable=False)
    motorista = db.Column(String(200), nullable=False)
    tipo_produto = db.Column(String(100), nullable=False, default='Triturado')
    quantidade_kg = db.Column(Float, nullable=False)
    lote = db.Column(Integer, nullable=False)  # 3 ou 5
    valor_carga = db.Column(Float, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pesagem {self.placa_veiculo} - {self.data}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'local_carga': self.local_carga,
            'local_descarga': self.local_descarga,
            'data': self.data.strftime('%d/%m/%Y'),
            'placa_veiculo': self.placa_veiculo,
            'motorista': self.motorista,
            'tipo_produto': self.tipo_produto,
            'quantidade_kg': self.quantidade_kg,
            'lote': self.lote,
            'valor_carga': self.valor_carga,
            'created_at': self.created_at
        }
