import os

from flask import Flask, jsonify, render_template_string, request
import mysql.connector


app = Flask(__name__)

# Configurações do MySQL vindas das variáveis de ambiente do container
DB_HOST = os.getenv('DB_HOST', 'mysqlsrv.mydomain.intra')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'usuarios')


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Cadastro de Usuários</title></head>
<body>
    <h2>Cadastrar Usuários</h2>
    <form method="POST">
        <label>Nome:</label><br>
        <input type="text" name="nome" required><br><br>
        <label>Idade:</label><br>
        <input type="number" name="idade" required><br><br>
        <button type="submit">Salvar</button>
    </form>
    {% if mensagem %}<p><b>{{ mensagem }}</b></p>{% endif %}
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    mensagem = ""

    if request.method == 'POST':
        nome = request.form.get('nome')
        idade = request.form.get('idade')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS pessoas "
                "(id INT AUTO_INCREMENT PRIMARY KEY, "
                "nome VARCHAR(255), idade INT)"
            )

            cursor.execute(
                "INSERT INTO pessoas (nome, idade) VALUES (%s, %s)",
                (nome, idade)
            )

            conn.commit()
            cursor.close()
            conn.close()

            mensagem = "Dados salvos com sucesso!"

        except Exception as e:
            mensagem = f"Erro ao salvar: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        mensagem=mensagem
    )


@app.route('/healthz', methods=['GET'])
def healthz():
    try:
        conn = get_db_connection()
        conn.ping(reconnect=False, attempts=1, delay=0)
        conn.close()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database_error": str(e)
        }), 500


@app.route('/livez', methods=['GET'])
def livez():
    return jsonify({"status": "alive"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
