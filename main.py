from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
import usuarios
import buscador
import ativos
import carteira
import calculadora
import gerador_grafico
import metas

app = Flask(__name__, static_folder='static')
app.secret_key = "fP$92wK@z_qXv*8jN"

database.iniciar_banco()

@app.route("/")
def homepage():
    return "Sistema de Investimentos Operacional."

@app.route("/cadastro", methods=["GET", "POST"])
def rota_cadastro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        if usuarios.cadastrar_usuario(nome, email, senha):
            flash(f"Bem-vindo, {nome}!", "success")
            return redirect(url_for("rota_login"))
        else:
            flash("Erro ao cadastrar.", "error")
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def rota_login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        usuario = usuarios.login(email, senha)
        if usuario:
            session['id_usuario'] = usuario['id']
            session['nome_usuario'] = usuario['nome']
            session['perfil_usuario'] = usuario['perfil']
            return redirect(url_for("dashboard"))
        else:
            flash("Dados incorretos.", "error")
    return render_template("login.html")

@app.route("/logout")
def rota_logout():
    session.clear()
    return redirect(url_for("rota_login"))

@app.route("/quiz", methods=["GET", "POST"])
def rota_quiz():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if request.method == "POST":
        pontuacao = 0
        for i in range(1, 6):
            r = request.form.get(f'p{i}')
            if r: pontuacao += int(r)
        perfil = "Conservador"
        if pontuacao >= 12: perfil = "Arrojado"
        elif pontuacao >= 9: perfil = "Moderado"
        usuarios.atualizar_perfil(session['id_usuario'], perfil)
        session['perfil_usuario'] = perfil
        flash(f"Perfil: {perfil}", "success")
        return redirect(url_for("dashboard"))
    return render_template("quiz.html")

@app.route("/deletar_conta")
def rota_deletar_conta():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    usuarios.deletar_usuario_completo(session['id_usuario'])
    session.clear()
    return redirect(url_for("homepage"))

@app.route("/dashboard")
def dashboard():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    return render_template("dashboard.html")

@app.route("/carteira")
def rota_carteira():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    dados_carteira = calculadora.calcular_desempenho_carteira(session['id_usuario'])
    return render_template("carteira.html", 
                           posicoes=dados_carteira['posicoes'], 
                           total_investido=dados_carteira['total_investido'],
                           total_atual=dados_carteira['total_atual'],
                           rendimento_total=dados_carteira['rendimento_total'])

@app.route("/acoes", methods=["GET", "POST"])
def rota_acoes():
    resultados = []
    termo = ""
    if request.method == "POST":
        termo = request.form.get('termo', '')
        resultados = buscador.buscar_ticker_por_nome(termo)
    else:
        resultados = buscador.get_todos_os_tickers()
    return render_template("acoes.html", resultados=resultados, termo=termo)

@app.route("/acao/<ticker>", methods=["GET", "POST"])
def rota_acao_detalhe(ticker):
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    ativo = ativos.get_or_create_ativo_by_ticker(ticker)
    if not ativo: return redirect(url_for('rota_acoes'))
    
    if request.method == "POST":
        valor = float(request.form['valor'])
        data = request.form['data']
        carteira.adicionar_posicao(session['id_usuario'], ativo['id'], valor, data)
        flash("Investimento adicionado!", "success")
        return redirect(url_for('rota_carteira'))
    
    caminho_grafico = gerador_grafico.gerar_grafico_anual(ticker)
    return render_template("acao_detalhe.html", ativo=ativo, grafico=caminho_grafico)

@app.route("/adicionar_renda_fixa", methods=["GET", "POST"])
def rota_adicionar_renda_fixa():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if request.method == "POST":
        nome = request.form['nome']
        tipo = request.form['tipo']
        perfil = request.form['perfil'] 
        valor = float(request.form['valor'])
        data = request.form['data']
        id_ativo = ativos.get_or_create_ativo_manual(nome, tipo, perfil)
        if id_ativo:
            carteira.adicionar_posicao(session['id_usuario'], id_ativo, valor, data)
            flash("Renda Fixa adicionada!", "success")
            return redirect(url_for('rota_carteira'))
    return render_template("adicionar_renda_fixa.html")

@app.route("/editar_posicao/<int:id_posicao>", methods=["GET", "POST"])
def rota_editar_posicao(id_posicao):
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if request.method == "POST":
        novo_valor = request.form['valor']
        nova_data = request.form['data']
        carteira.editar_posicao(id_posicao, novo_valor, nova_data)
        flash("Atualizado.", "success")
        return redirect(url_for('rota_carteira'))
    posicao = carteira.get_posicao_por_id(id_posicao)
    return render_template("editar_posicao.html", posicao=posicao)

@app.route("/vender_posicao/<int:id_posicao>")
def rota_vender_posicao(id_posicao):
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if carteira.deletar_posicao_web(id_posicao, session['id_usuario']):
        flash("Posição vendida.", "success")
    else:
        flash("Erro ao remover.", "error")
    return redirect(url_for('rota_carteira'))

@app.route("/metas", methods=["GET", "POST"])
def rota_metas():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if request.method == "POST":
        titulo = request.form['titulo']
        valor = float(request.form['valor'])
        data = request.form['data']
        metas.criar_meta(session['id_usuario'], titulo, valor, data)
        flash("Meta criada com sucesso!", "success")
    
    minhas_metas = metas.listar_metas(session['id_usuario'])
    return render_template("metas.html", metas=minhas_metas)

@app.route("/deletar_meta/<int:id_meta>")
def rota_deletar_meta(id_meta):
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    metas.deletar_meta(id_meta)
    flash("Meta removida.", "info")
    return redirect(url_for('rota_metas'))

if __name__ == "__main__":
    app.run(debug=True)
