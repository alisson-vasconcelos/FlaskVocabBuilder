from flask import render_template, request, redirect, url_for, flash, make_response, send_file
from app import app, db
from models import Pesagem
from utils import calcular_lote_e_valor, gerar_ticket_pdf, gerar_relatorio_excel
from datetime import datetime
import os
import tempfile

@app.route('/')
def index():
    """Página inicial com lista de pesagens"""
    pesagens = Pesagem.query.order_by(Pesagem.created_at.desc()).all()
    return render_template('index.html', pesagens=pesagens)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Formulário de registro de pesagem"""
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            local_carga = request.form.get('local_carga').strip()
            local_descarga = request.form.get('local_descarga').strip()
            data_str = request.form.get('data')
            placa_veiculo = request.form.get('placa_veiculo').strip().upper()
            motorista = request.form.get('motorista').strip()
            quantidade_kg = float(request.form.get('quantidade_kg', 0))
            
            # Validações básicas
            if not all([local_carga, local_descarga, data_str, placa_veiculo, motorista]):
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template('registro.html')
            
            if quantidade_kg <= 0:
                flash('A quantidade deve ser maior que zero!', 'error')
                return render_template('registro.html')
            
            # Converter data
            data = datetime.strptime(data_str, '%Y-%m-%d')
            
            # Calcular lote e valor
            lote, valor_carga = calcular_lote_e_valor(local_carga, quantidade_kg)
            
            if lote is None:
                flash('Local de carga não encontrado na lista de cidades cadastradas!', 'error')
                return render_template('registro.html')
            
            # Criar novo registro
            nova_pesagem = Pesagem(
                local_carga=local_carga,
                local_descarga=local_descarga,
                data=data,
                placa_veiculo=placa_veiculo,
                motorista=motorista,
                tipo_produto='Triturado',
                quantidade_kg=quantidade_kg,
                lote=lote,
                valor_carga=valor_carga
            )
            
            db.session.add(nova_pesagem)
            db.session.commit()
            
            flash('Pesagem registrada com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash('Erro nos dados fornecidos. Verifique os campos numéricos e de data.', 'error')
        except Exception as e:
            flash(f'Erro ao salvar registro: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('registro.html')

@app.route('/ticket/<int:pesagem_id>')
def ticket(pesagem_id):
    """Visualizar ticket de pesagem"""
    pesagem = Pesagem.query.get_or_404(pesagem_id)
    return render_template('ticket.html', pesagem=pesagem)

@app.route('/ticket/<int:pesagem_id>/pdf')
def ticket_pdf(pesagem_id):
    """Gerar PDF do ticket de pesagem"""
    pesagem = Pesagem.query.get_or_404(pesagem_id)
    
    # Gerar PDF em arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        gerar_ticket_pdf(pesagem, tmp_file.name)
        
        # Enviar arquivo
        response = make_response(send_file(tmp_file.name, as_attachment=True, 
                                         download_name=f'ticket_pesagem_{pesagem.placa_veiculo}_{pesagem.data.strftime("%Y%m%d")}.pdf'))
        
        # Agendar limpeza do arquivo temporário
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(tmp_file.name)
            except:
                pass
        
        return response

@app.route('/relatorio/excel')
def relatorio_excel():
    """Gerar relatório em Excel"""
    pesagens = Pesagem.query.order_by(Pesagem.data.desc()).all()
    
    if not pesagens:
        flash('Nenhuma pesagem encontrada para gerar relatório!', 'warning')
        return redirect(url_for('index'))
    
    # Gerar Excel em arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        gerar_relatorio_excel(pesagens, tmp_file.name)
        
        # Enviar arquivo
        response = make_response(send_file(tmp_file.name, as_attachment=True, 
                                         download_name=f'relatorio_pesagens_{datetime.now().strftime("%Y%m%d")}.xlsx'))
        
        # Agendar limpeza do arquivo temporário
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(tmp_file.name)
            except:
                pass
        
        return response

@app.route('/relatorio/csv')
def relatorio_csv():
    """Gerar relatório em CSV"""
    pesagens = Pesagem.query.order_by(Pesagem.data.desc()).all()
    
    if not pesagens:
        flash('Nenhuma pesagem encontrada para gerar relatório!', 'warning')
        return redirect(url_for('index'))
    
    # Gerar CSV
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['Placa', 'Motorista', 'Cidade (Local de Carga)', 'Lote', 'Data da Descarga', 'Kg (Quilos)', 'Valor da Carga'])
    
    # Dados
    for pesagem in pesagens:
        writer.writerow([
            pesagem.placa_veiculo,
            pesagem.motorista,
            pesagem.local_carga,
            f'Lote {pesagem.lote}',
            pesagem.data.strftime('%d/%m/%Y'),
            pesagem.quantidade_kg,
            f'R$ {pesagem.valor_carga:.2f}'
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_pesagens_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
