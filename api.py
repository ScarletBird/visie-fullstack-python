from flask import Flask, render_template, make_response
from flask_restful import Resource, Api, reqparse, abort

import datetime
import mysql.connector

app = Flask(__name__)
api = Api(app)

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("nome", type=str, help="Nome da pessoa", required=True)
task_post_args.add_argument("data_admissao", type=str, help="Data de admissao", required=True)

# Função que retorna a conexão com o banco de dados, para evitar repetição
def connectDB():
    return mysql.connector.connect(user='visie_user', password='visie_pass',
                                   host='db4free.net',
                                   database='visie_db')

def getDB():
    db = connectDB()
    nomesDict = {}

    try:
        cursor = db.cursor()
        cursor.execute('SELECT id_pessoa, nome, data_admissao  FROM pessoas')
        selectNomes = cursor.fetchall()
        
        i = 1
        for n in selectNomes:
            nomesDict[i] = {
                "id": i,
                "id_pessoa": n[0],
                "nome": n[1].split(' ')[0] ,
                "data_admissao": str(n[2].day) + "/" + str(n[2].month) + "/" + str(n[2].year)
                }
            i = i + 1
        #print(nomesDict)
        
        cursor.close()

    except:
        print("Erro na conexão com o banco de dados!")

    finally:
        db.close()

    return nomesDict

def addDB(nome, data_admissao):
    db = connectDB()

    try:
        cursor = db.cursor()
        sql = "INSERT INTO pessoas (nome, data_admissao) VALUES (%s, %s)"
        val = (nome, datetime.datetime.strptime(data_admissao,"%Y-%m-%d").date())
        cursor.execute(sql, val)

        db.commit()
 
        print(cursor.rowcount, "record(s) inserted")
        cursor.close()

    except:
        print("Erro na conexão com o banco de dados!")
        
    finally:
        db.close()


def deleteDB(id):
    db = connectDB()
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM pessoas WHERE id_pessoa = {}'.format(id))

        db.commit()

        print(cursor.rowcount, "record(s) deleted")
        cursor.close()

    except:
        print("Erro na conexão com o banco de dados!")

    finally:
        db.close()

class Pessoas(Resource):
    # GET captura a lista de todas as pessoas e retorna o html principal no localhost:5000
    def get(self):
        dict = getDB()
        return make_response(render_template('index.html', nomes=dict.values()))
    # POST insere uma nova pessoa na database, usando o formulário do HTML (ou dados enviados)
    def post(self):
        args = task_post_args.parse_args()
        addDB(args["nome"], args["data_admissao"])


class Pessoa(Resource):
    # GET captura uma única pessoa (não utilizada no HTML)
    def get(self, id):
        return getDB()[id]
    # POST deleta uma pessoa (foi tentado utilizar o método DELETE, mas seria necessário script
    # e para deixar o desafio o mais puro em HTML, foi feito com POST)
    def post(self, id):
        deleteDB(id)


api.add_resource(Pessoas, '/pessoas')
api.add_resource(Pessoa, '/pessoas/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)