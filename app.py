import os
from flask import Flask, render_template, request, redirect, url_for, session
import csv

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'uma-chave-secreta-padrao')
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Lista de quizzes padrão (nome do arquivo na pasta quizzes)
QUIZZES_PADRAO = {
    'Matemática': 'matematica.txt',
    'Português': 'portugues.txt',
    'Ciências': 'ciencias.txt',
    'Geografia': 'geografia.txt',
    'História': 'historia.txt',
    'Inglês': 'ingles.txt',
    'Educação Física': 'educacao_fisica.txt',
    'Arte': 'arte.txt',
    'Música': 'musica.txt',
    'Redação': 'redacao.txt',
    'Orientação Humana': 'orientacao_humana.txt'
    'A': 'Arquivo_de_texto.txt'
}

def ler_perguntas(caminho_arquivo):
    """Lê o arquivo CSV e retorna lista de dicionários."""
    perguntas = []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            perguntas.append({
                "texto": linha["texto"],
                "opcoes": [linha["opcao_a"], linha["opcao_b"], linha["opcao_c"], linha["opcao_d"]],
                "resposta": int(linha["resposta"])
            })
    return perguntas

@app.route('/', methods=['GET', 'POST'])
def index():
    """Tela inicial: upload de arquivo ou escolha de quiz padrão."""
    if request.method == 'POST':
        # Upload de arquivo
        arquivo = request.files.get('arquivo')
        if arquivo and arquivo.filename.endswith(('.txt', '.csv')):
            from werkzeug.utils import secure_filename
            nome_seguro = secure_filename(arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
            arquivo.save(caminho)
            perguntas = ler_perguntas(caminho)
            session['perguntas'] = perguntas
            session['indice'] = 0
            session['acertos'] = 0
            session['erros'] = 0
            return redirect(url_for('quiz'))
    return render_template('index.html', quizzes=QUIZZES_PADRAO)

@app.route('/padrao/<materia>')
def quiz_padrao(materia):
    """Carrega um quiz padrão a partir dos arquivos da pasta quizzes."""
    if materia in QUIZZES_PADRAO:
        caminho = os.path.join('quizzes', QUIZZES_PADRAO[materia])
        if os.path.exists(caminho):
            perguntas = ler_perguntas(caminho)
            session['perguntas'] = perguntas
            session['indice'] = 0
            session['acertos'] = 0
            session['erros'] = 0
            return redirect(url_for('quiz'))
    return redirect(url_for('index'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Exibe pergunta atual e processa resposta."""
    if 'perguntas' not in session:
        return redirect(url_for('index'))

    perguntas = session['perguntas']
    indice = session['indice']

    if request.method == 'POST':
        escolha = request.form.get('escolha')
        if escolha:
            resposta_correta = perguntas[indice]['resposta']
            if int(escolha) == resposta_correta:
                session['acertos'] += 1
            else:
                session['erros'] += 1
        session['indice'] += 1
        indice = session['indice']

    if indice >= len(perguntas):
        return redirect(url_for('resultado'))

    pergunta_atual = perguntas[indice]
    return render_template('quiz.html',
                           pergunta=pergunta_atual,
                           indice=indice+1,
                           total=len(perguntas),
                           acertos=session['acertos'],
                           erros=session['erros'])

@app.route('/resultado')
def resultado():
    """Exibe a pontuação final."""
    if 'perguntas' not in session:
        return redirect(url_for('index'))

    total = len(session['perguntas'])
    acertos = session['acertos']
    erros = session['erros']
    percentual = (acertos / total) * 100 if total else 0

    session.clear()
    return render_template('resultado.html',
                           acertos=acertos,
                           erros=erros,
                           total=total,
                           percentual=percentual)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
