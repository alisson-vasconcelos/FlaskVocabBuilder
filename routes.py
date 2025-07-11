from flask import render_template, request, redirect, url_for, flash, make_response, send_file, jsonify
from app import app, db
from models import Pesagem, Veiculo
from utils import calcular_lote_e_valor, gerar_ticket_pdf, gerar_relatorio_excel
from datetime import datetime
import os
import tempfile

@app.route('/')
def index():
    """Página inicial com lista de pesagens"""
    # Obter parâmetros de filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    lote = request.args.get('lote')
    placa = request.args.get('placa')
    veiculo_id = request.args.get('veiculo_id')
    
    # Construir query com filtros
    query = Pesagem.query
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Pesagem.data >= data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Pesagem.data <= data_fim_obj)
        except ValueError:
            pass
    
    if lote and lote.isdigit():
        query = query.filter(Pesagem.lote == int(lote))
    
    if placa:
        query = query.filter(Pesagem.placa_veiculo.ilike(f'%{placa}%'))
    
    if veiculo_id and veiculo_id.isdigit():
        query = query.filter(Pesagem.veiculo_id == int(veiculo_id))
    
    pesagens = query.order_by(Pesagem.created_at.desc()).all()
    veiculos_ativos = Veiculo.query.filter_by(ativo=True).order_by(Veiculo.placa).all()
    
    return render_template('index.html', pesagens=pesagens, 
                         data_inicio=data_inicio, data_fim=data_fim, 
                         lote=lote, placa=placa, veiculo_id=veiculo_id,
                         veiculos_ativos=veiculos_ativos)

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
                return render_template('registro.html', veiculos=Veiculo.query.filter_by(ativo=True).all())
            
            if quantidade_kg <= 0:
                flash('A quantidade deve ser maior que zero!', 'error')
                return render_template('registro.html', veiculos=Veiculo.query.filter_by(ativo=True).all())
            
            # Converter data
            data = datetime.strptime(data_str, '%Y-%m-%d')
            
            # Calcular lote e valor
            lote, valor_carga = calcular_lote_e_valor(local_carga, quantidade_kg)
            
            if lote is None:
                flash('Local de carga não encontrado na lista de cidades cadastradas!', 'error')
                return render_template('registro.html', veiculos=Veiculo.query.filter_by(ativo=True).all())
            
            # Buscar veículo pelo placa
            veiculo = Veiculo.query.filter_by(placa=placa_veiculo).first()
            
            # Criar novo registro
            nova_pesagem = Pesagem(
                local_carga=local_carga,
                local_descarga=local_descarga,
                data=data,
                placa_veiculo=placa_veiculo,
                veiculo_id=veiculo.id if veiculo else None,
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
    
    veiculos = Veiculo.query.filter_by(ativo=True).all()
    return render_template('registro.html', veiculos=veiculos)

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
    # Obter parâmetros de filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    lote = request.args.get('lote')
    placa = request.args.get('placa')
    veiculo_id = request.args.get('veiculo_id')
    
    # Construir query com filtros
    query = Pesagem.query
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Pesagem.data >= data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Pesagem.data <= data_fim_obj)
        except ValueError:
            pass
    
    if lote and lote.isdigit():
        query = query.filter(Pesagem.lote == int(lote))
    
    if placa:
        query = query.filter(Pesagem.placa_veiculo.ilike(f'%{placa}%'))
    
    if veiculo_id and veiculo_id.isdigit():
        query = query.filter(Pesagem.veiculo_id == int(veiculo_id))
    
    pesagens = query.order_by(Pesagem.data.desc()).all()
    
    if not pesagens:
        flash('Nenhuma pesagem encontrada para gerar relatório!', 'warning')
        return redirect(url_for('index'))
    
    # Gerar Excel em arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        gerar_relatorio_excel(pesagens, tmp_file.name)
        
        # Nome do arquivo com filtros
        filename_suffix = datetime.now().strftime("%Y%m%d")
        if data_inicio or data_fim or lote or placa or veiculo_id:
            filename_suffix += "_filtrado"
        
        # Enviar arquivo
        response = make_response(send_file(tmp_file.name, as_attachment=True, 
                                         download_name=f'relatorio_pesagens_{filename_suffix}.xlsx'))
        
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
    # Obter parâmetros de filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    lote = request.args.get('lote')
    placa = request.args.get('placa')
    veiculo_id = request.args.get('veiculo_id')
    
    # Construir query com filtros
    query = Pesagem.query
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Pesagem.data >= data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Pesagem.data <= data_fim_obj)
        except ValueError:
            pass
    
    if lote and lote.isdigit():
        query = query.filter(Pesagem.lote == int(lote))
    
    if placa:
        query = query.filter(Pesagem.placa_veiculo.ilike(f'%{placa}%'))
    
    if veiculo_id and veiculo_id.isdigit():
        query = query.filter(Pesagem.veiculo_id == int(veiculo_id))
    
    pesagens = query.order_by(Pesagem.data.desc()).all()
    
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
    
    # Nome do arquivo com filtros
    filename_suffix = datetime.now().strftime("%Y%m%d")
    if data_inicio or data_fim or lote or placa or veiculo_id:
        filename_suffix += "_filtrado"
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_pesagens_{filename_suffix}.csv'
    
    return response

@app.route('/veiculos')
def veiculos():
    """Página de gerenciamento de veículos"""
    veiculos = Veiculo.query.order_by(Veiculo.created_at.desc()).all()
    return render_template('veiculos.html', veiculos=veiculos)

@app.route('/veiculos/novo', methods=['GET', 'POST'])
def novo_veiculo():
    """Formulário para cadastrar novo veículo"""
    if request.method == 'POST':
        try:
            placa = request.form.get('placa').strip().upper()
            modelo = request.form.get('modelo').strip()
            marca = request.form.get('marca').strip()
            ano = request.form.get('ano')
            cor = request.form.get('cor').strip()
            motorista_padrao = request.form.get('motorista_padrao').strip()
            
            # Validações
            if not all([placa, modelo, marca]):
                flash('Placa, modelo e marca são obrigatórios!', 'error')
                return render_template('novo_veiculo.html')
            
            # Verificar se placa já existe
            if Veiculo.query.filter_by(placa=placa).first():
                flash('Já existe um veículo cadastrado com esta placa!', 'error')
                return render_template('novo_veiculo.html')
            
            # Criar novo veículo
            novo_veiculo = Veiculo(
                placa=placa,
                modelo=modelo,
                marca=marca,
                ano=int(ano) if ano else None,
                cor=cor if cor else None,
                motorista_padrao=motorista_padrao if motorista_padrao else None
            )
            
            db.session.add(novo_veiculo)
            db.session.commit()
            
            flash('Veículo cadastrado com sucesso!', 'success')
            return redirect(url_for('veiculos'))
            
        except ValueError as e:
            flash('Erro nos dados fornecidos. Verifique o ano do veículo.', 'error')
        except Exception as e:
            flash(f'Erro ao salvar veículo: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('novo_veiculo.html')

@app.route('/veiculos/<int:veiculo_id>/editar', methods=['GET', 'POST'])
def editar_veiculo(veiculo_id):
    """Editar veículo existente"""
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    
    if request.method == 'POST':
        try:
            veiculo.placa = request.form.get('placa').strip().upper()
            veiculo.modelo = request.form.get('modelo').strip()
            veiculo.marca = request.form.get('marca').strip()
            ano = request.form.get('ano')
            veiculo.ano = int(ano) if ano else None
            veiculo.cor = request.form.get('cor').strip() or None
            veiculo.motorista_padrao = request.form.get('motorista_padrao').strip() or None
            
            # Validações
            if not all([veiculo.placa, veiculo.modelo, veiculo.marca]):
                flash('Placa, modelo e marca são obrigatórios!', 'error')
                return render_template('editar_veiculo.html', veiculo=veiculo)
            
            # Verificar se placa já existe (excluindo o próprio veículo)
            veiculo_existente = Veiculo.query.filter_by(placa=veiculo.placa).first()
            if veiculo_existente and veiculo_existente.id != veiculo.id:
                flash('Já existe outro veículo cadastrado com esta placa!', 'error')
                return render_template('editar_veiculo.html', veiculo=veiculo)
            
            db.session.commit()
            flash('Veículo atualizado com sucesso!', 'success')
            return redirect(url_for('veiculos'))
            
        except ValueError as e:
            flash('Erro nos dados fornecidos. Verifique o ano do veículo.', 'error')
        except Exception as e:
            flash(f'Erro ao atualizar veículo: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('editar_veiculo.html', veiculo=veiculo)

@app.route('/veiculos/<int:veiculo_id>/toggle-status', methods=['POST'])
def toggle_veiculo_status(veiculo_id):
    """Ativar/desativar veículo"""
    veiculo = Veiculo.query.get_or_404(veiculo_id)
    veiculo.ativo = not veiculo.ativo
    db.session.commit()
    
    status = 'ativado' if veiculo.ativo else 'desativado'
    flash(f'Veículo {status} com sucesso!', 'success')
    return redirect(url_for('veiculos'))

@app.route('/api/veiculo/<placa>')
def get_veiculo_info(placa):
    """API para obter informações do veículo pela placa"""
    veiculo = Veiculo.query.filter_by(placa=placa.upper()).first()
    if veiculo:
        return jsonify({
            'exists': True,
            'motorista_padrao': veiculo.motorista_padrao,
            'modelo': veiculo.modelo,
            'marca': veiculo.marca
        })
    return jsonify({'exists': False})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
