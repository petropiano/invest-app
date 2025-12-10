from flask import Flask, render_template, request, redirect, url_for, flash, session
import database
import usuarios
import buscador
import ativos

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
            flash(f"Bem-vindo, {nome}! Faça login para continuar.", "success")
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
            flash("Email ou senha incorretos.", "error")
    return render_template("login.html")

@app.route("/logout")
def rota_logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("rota_login"))

@app.route("/quiz", methods=["GET", "POST"])
def rota_quiz():
    if 'id_usuario' not in session:
        return redirect(url_for('rota_login'))
    if request.method == "POST":
        pontuacao = 0
        for i in range(1, 6):
            resposta = request.form.get(f'p{i}')
            if resposta: pontuacao += int(resposta)
        perfil = "Conservador"
        if pontuacao >= 12: perfil = "Arrojado"
        elif pontuacao >= 9: perfil = "Moderado"
        usuarios.atualizar_perfil(session['id_usuario'], perfil)
        session['perfil_usuario'] = perfil
        flash(f"Seu perfil foi definido como: {perfil}", "success")
        return redirect(url_for("dashboard"))
    return render_template("quiz.html")

@app.route("/deletar_conta")
def rota_deletar_conta():
    if 'id_usuario' not in session: return redirect(url_for('rota_login'))
    if usuarios.deletar_usuario_completo(session['id_usuario']):
        session.clear()
        flash("Conta excluída.", "info")
        return redirect(url_for("homepage"))
    else:
        flash("Erro ao excluir.", "error")
        return redirect(url_for("dashboard"))

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
    if 'id_usuario' not in session:
        return redirect(url_for('rota_login'))

    ativo = ativos.get_or_create_ativo_by_ticker(ticker)
    
    if not ativo:
        flash(f"Dados não encontrados para {ticker}", "error")
        return redirect(url_for('rota_acoes'))
    
    return render_template("acao_detalhe.html", ativo=ativo)

if __name__ == "__main__":
    app.run(debug=True)
