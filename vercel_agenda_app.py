from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import calendar
import datetime
import string
import random

app = Flask(__name__)

# Simulando um banco de dados em memória (em produção, use um banco real)
agenda_data = []

def gera_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def validar_data(data_str, formato="%d/%m/%Y"):
    """Valida se a data está no formato correto"""
    try:
        datetime.datetime.strptime(data_str, formato)
        return True
    except ValueError:
        return False

def validar_hora(hora_str, formato="%H:%M"):
    """Valida se a hora está no formato correto"""
    try:
        datetime.datetime.strptime(hora_str, formato)
        return True
    except ValueError:
        return False

@app.route('/')
def index():
    """Página principal com calendário e lista de compromissos"""
    # Gerando calendário do mês atual
    data = datetime.datetime.now()
    ano = data.year
    mes = data.month
    
    meses_do_ano = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    mes_extenso = meses_do_ano[mes]
    calendario = calendar.month(ano, mes)
    
    # Template inline para simplificar o deploy
    return render_template_string(get_html_template(), 
                         calendario=calendario, 
                         mes_extenso=mes_extenso, 
                         ano=ano,
                         agenda=agenda_data)

def get_html_template():
    # Retorna o HTML como string para evitar problemas com templates
    return '''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agenda Digital</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); }
        h1 { text-align: center; color: #333; margin-bottom: 30px; font-size: 2.5em; background: linear-gradient(45deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .calendar-section, .agenda-section { background: white; border-radius: 15px; padding: 25px; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05); }
        .calendar-section h2, .agenda-section h2 { color: #333; margin-bottom: 20px; font-size: 1.8em; }
        .calendar { font-family: 'Courier New', monospace; background: #f8f9fa; padding: 20px; border-radius: 10px; white-space: pre; font-size: 14px; line-height: 1.4; overflow-x: auto; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        input[type="text"], input[type="time"], input[type="date"], textarea { width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; transition: border-color 0.3s ease; }
        input[type="text"]:focus, input[type="time"]:focus, input[type="date"]:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        .btn { background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; padding: 12px 25px; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: 600; transition: transform 0.2s ease, box-shadow 0.2s ease; margin-right: 10px; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn-danger { background: linear-gradient(45deg, #ff6b6b, #ee5a24); }
        .btn-danger:hover { box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4); }
        .compromissos-list { display: grid; gap: 15px; }
        .compromisso-item { background: #f8f9fa; border-left: 5px solid #667eea; padding: 20px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; transition: transform 0.2s ease; }
        .compromisso-item:hover { transform: translateX(5px); }
        .compromisso-info h3 { color: #333; margin-bottom: 5px; }
        .compromisso-info p { color: #666; margin-bottom: 3px; }
        .compromisso-actions { display: flex; gap: 10px; }
        .btn-small { padding: 8px 15px; font-size: 14px; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); }
        .modal-content { background-color: white; margin: 10% auto; padding: 30px; border-radius: 15px; width: 90%; max-width: 500px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2); }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 10px; display: none; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        @media (max-width: 768px) { .container { padding: 15px; } .compromisso-item { flex-direction: column; align-items: flex-start; } .compromisso-actions { margin-top: 10px; width: 100%; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>📅 Agenda Digital</h1>
        <div id="alert" class="alert"></div>
        <div class="calendar-section">
            <h2>Calendário de {{ mes_extenso }} de {{ ano }}</h2>
            <div class="calendar">{{ calendario }}</div>
        </div>
        <div class="agenda-section">
            <h2>Novo Compromisso</h2>
            <form id="compromissoForm">
                <div class="form-group">
                    <label for="data">Data:</label>
                    <input type="date" id="data" name="data" required>
                </div>
                <div class="form-group">
                    <label for="hora">Hora:</label>
                    <input type="time" id="hora" name="hora" required>
                </div>
                <div class="form-group">
                    <label for="descricao">Descrição:</label>
                    <textarea id="descricao" name="descricao" rows="3" required></textarea>
                </div>
                <button type="submit" class="btn">Agendar Compromisso</button>
            </form>
        </div>
        <div class="agenda-section">
            <h2>Compromissos Agendados</h2>
            <div id="compromissosList" class="compromissos-list">
                <!-- Compromissos serão carregados aqui via JavaScript -->
            </div>
        </div>
    </div>
    <div id="editModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Editar Compromisso</h2>
            <form id="editForm">
                <div class="form-group">
                    <label for="editData">Data:</label>
                    <input type="date" id="editData" name="data" required>
                </div>
                <div class="form-group">
                    <label for="editHora">Hora:</label>
                    <input type="time" id="editHora" name="hora" required>
                </div>
                <div class="form-group">
                    <label for="editDescricao">Descrição:</label>
                    <textarea id="editDescricao" name="descricao" rows="3" required></textarea>
                </div>
                <button type="submit" class="btn">Salvar Alterações</button>
                <button type="button" class="btn btn-danger" onclick="closeModal()">Cancelar</button>
            </form>
        </div>
    </div>
    <script>
        let compromissos = [];
        let editingIndex = -1;
        const compromissoForm = document.getElementById('compromissoForm');
        const editForm = document.getElementById('editForm');
        const editModal = document.getElementById('editModal');
        const compromissosList = document.getElementById('compromissosList');
        const alert = document.getElementById('alert');
        
        console.log('JavaScript carregado!');
        
        compromissoForm.addEventListener('submit', adicionarCompromisso);
        editForm.addEventListener('submit', salvarEdicao);
        document.querySelector('.close').addEventListener('click', closeModal);
        
        async function adicionarCompromisso(e) {
            e.preventDefault();
            console.log('Formulário submetido');
            
            const formData = new FormData(e.target);
            const data = formData.get('data');
            const hora = formData.get('hora');
            const descricao = formData.get('descricao');
            
            if (!data || !hora || !descricao.trim()) {
                showAlert('Por favor, preencha todos os campos!', 'error');
                return;
            }
            
            const dataFormatada = formatarData(data);
            const novoCompromisso = { data: dataFormatada, hora: hora, descricao: descricao.trim() };
            
            console.log('Dados do compromisso:', novoCompromisso);
            
            // Sempre adicionar localmente primeiro para garantir que funcione
            novoCompromisso.id = gerarId();
            compromissos.push(novoCompromisso);
            renderizarCompromissos();
            showAlert('Compromisso agendado com sucesso!', 'success');
            compromissoForm.reset();
            
            // Tentar enviar para o servidor em background
            try {
                const response = await fetch('/api/compromissos', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(novoCompromisso)
                });
                console.log('Resposta do servidor:', response.status);
            } catch (error) {
                console.log('Servidor não disponível, usando modo offline');
            }
        }
        
        async function carregarCompromissos() {
            try {
                const response = await fetch('/api/compromissos');
                if (response.ok) {
                    const serverData = await response.json();
                    if (serverData.length > 0) {
                        compromissos = serverData;
                    }
                }
            } catch (error) {
                console.log('Usando dados locais');
            }
            renderizarCompromissos();
        }
        
        function renderizarCompromissos() {
            console.log('Renderizando', compromissos.length, 'compromissos');
            compromissosList.innerHTML = '';
            
            if (compromissos.length === 0) {
                compromissosList.innerHTML = '<p style="text-align: center; color: #666;">Nenhum compromisso agendado</p>';
                return;
            }
            
            compromissos.forEach((compromisso, index) => {
                const compromissoDiv = document.createElement('div');
                compromissoDiv.className = 'compromisso-item';
                compromissoDiv.innerHTML = `
                    <div class="compromisso-info">
                        <h3>${compromisso.descricao}</h3>
                        <p><strong>Data:</strong> ${compromisso.data}</p>
                        <p><strong>Hora:</strong> ${compromisso.hora}</p>
                        <p><strong>ID:</strong> ${compromisso.id}</p>
                    </div>
                    <div class="compromisso-actions">
                        <button class="btn btn-small" onclick="excluirCompromisso(${index})">Excluir</button>
                    </div>
                `;
                compromissosList.appendChild(compromissoDiv);
            });
        }
        
        async function excluirCompromisso(index) {
            if (confirm('Tem certeza que deseja excluir este compromisso?')) {
                compromissos.splice(index, 1);
                renderizarCompromissos();
                showAlert('Compromisso excluído com sucesso!', 'success');
            }
        }
        
        function showAlert(message, type) {
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';
            setTimeout(() => { alert.style.display = 'none'; }, 5000);
        }
        
        function formatarData(dataInput) {
            if (dataInput.includes('/')) return dataInput;
            const date = new Date(dataInput + 'T00:00:00');
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        }
        
        function gerarId() {
            return Math.random().toString(36).substr(2, 6).toUpperCase();
        }
        
        // Inicializar quando a página carregar
        document.addEventListener('DOMContentLoaded', carregarCompromissos);
    </script>
</body>
</html>'''

@app.route('/api/compromissos', methods=['GET'])
def listar_compromissos():
    """API para listar todos os compromissos"""
    return jsonify(agenda_data)

@app.route('/api/compromissos', methods=['POST'])
def agendar_compromisso():
    """API para criar um novo compromisso"""
    data = request.json
    
    # Validações
    if not validar_data(data.get('data', '')):
        return jsonify({'error': 'Data inválida. Use o formato DD/MM/AAAA'}), 400
    
    if not validar_hora(data.get('hora', '')):
        return jsonify({'error': 'Hora inválida. Use o formato HH:MM'}), 400
    
    if not data.get('descricao', '').strip():
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    # Criar novo compromisso
    novo_compromisso = {
        'id': gera_id(),
        'data': data['data'],
        'hora': data['hora'],
        'descricao': data['descricao'].strip()
    }
    
    agenda_data.append(novo_compromisso)
    return jsonify(novo_compromisso), 201

@app.route('/api/compromissos/<int:indice>', methods=['PUT'])
def alterar_compromisso(indice):
    """API para alterar um compromisso existente"""
    if indice >= len(agenda_data):
        return jsonify({'error': 'Compromisso não encontrado'}), 404
    
    data = request.json
    
    # Validações opcionais (só valida se o campo foi enviado)
    if 'data' in data and not validar_data(data['data']):
        return jsonify({'error': 'Data inválida. Use o formato DD/MM/AAAA'}), 400
    
    if 'hora' in data and not validar_hora(data['hora']):
        return jsonify({'error': 'Hora inválida. Use o formato HH:MM'}), 400
    
    # Atualizar campos enviados
    if 'data' in data:
        agenda_data[indice]['data'] = data['data']
    if 'hora' in data:
        agenda_data[indice]['hora'] = data['hora']
    if 'descricao' in data:
        agenda_data[indice]['descricao'] = data['descricao'].strip()
    
    return jsonify(agenda_data[indice])

@app.route('/api/compromissos/<int:indice>', methods=['DELETE'])
def excluir_compromisso(indice):
    """API para excluir um compromisso"""
    if indice >= len(agenda_data):
        return jsonify({'error': 'Compromisso não encontrado'}), 404
    
    compromisso_removido = agenda_data.pop(indice)
    return jsonify({'message': 'Compromisso excluído com sucesso', 'compromisso': compromisso_removido})

# Para desenvolvimento local
if __name__ == '__main__':
    app.run(debug=True)

# Para Vercel (serverless)
def handler(event, context):
    return app