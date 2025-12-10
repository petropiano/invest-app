from flask import Flask
import database

app = Flask(__name__, static_folder='static')
app.secret_key = "fP$92wK@z_qXv*8jN"

database.iniciar_banco()

@app.route("/")
def homepage():
    return "Sistema de Investimentos Operacional."

if __name__ == "__main__":
    app.run(debug=True)
