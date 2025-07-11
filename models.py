from app import db
from datetime import datetime
from sqlalchemy import DateTime, String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

class Veiculo(db.Model):
    """Modelo para armazenar os dados dos veículos"""
    id = db.Column(Integer, primary_key=True)
    placa = db.Column(String(20), nullable=False, unique=True)
    modelo = db.Column(String(100), nullable=False)
    marca = db.Column(String(100), nullable=False)
    ano = db.Column(Integer, nullable=True)
    cor = db.Column(String(50), nullable=True)
    motorista_padrao = db.Column(String(200), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com pesagens
    pesagens = relationship('Pesagem', back_populates='veiculo')
    
    def __repr__(self):
        return f'<Veiculo {self.placa} - {self.marca} {self.modelo}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'placa': self.placa,
            'modelo': self.modelo,
            'marca': self.marca,
            'ano': self.ano,
            'cor': self.cor,
            'motorista_padrao': self.motorista_padrao,
            'ativo': self.ativo,
            'created_at': self.created_at
        }

class Pesagem(db.Model):
    """Modelo para armazenar os dados de pesagem dos caminhões"""
    id = db.Column(Integer, primary_key=True)
    local_carga = db.Column(String(200), nullable=False)
    local_descarga = db.Column(String(200), nullable=False)
    data = db.Column(DateTime, nullable=False)
    placa_veiculo = db.Column(String(20), nullable=False)
    veiculo_id = db.Column(Integer, ForeignKey('veiculo.id'), nullable=True)
    motorista = db.Column(String(200), nullable=False)
    tipo_produto = db.Column(String(100), nullable=False, default='Triturado')
    quantidade_kg = db.Column(Float, nullable=False)
    lote = db.Column(Integer, nullable=False)  # 3 ou 5
    valor_carga = db.Column(Float, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento com veículo
    veiculo = relationship('Veiculo', back_populates='pesagens')
    
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
