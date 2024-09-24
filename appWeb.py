from flask import Flask
import pymongo


app = Flask(__name__)

app.secret_key="secret_key"


app.config['UPLOAD_FOLDER']='./static/imG'

miConexion = pymongo.MongoClient("mongodb://localhost:27017/")

baseDatos = miConexion['tienda']

productos = baseDatos['producto']

usuarios = baseDatos['usuarios']

if __name__=="__main__":
    from Controller.productoController import *
    from Controller.usuarioController import * 
    
    app.run(port=4004,debug=True)
    
    