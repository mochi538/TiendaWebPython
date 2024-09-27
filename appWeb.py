from flask import Flask
import pymongo


app = Flask(__name__)

app.secret_key="secret_key"


app.config['UPLOAD_FOLDER']='./static/imG'

miConexion = pymongo.MongoClient("mongodb+srv://mochi5384:AALTBTPX_X@cluster0.rkfo3qm.mongodb.net/Tienda?retryWrites=true&w=majority&appName=Cluster0")

baseDatos = miConexion['Tienda']

productos = baseDatos['Productos']

usuarios = baseDatos['Usuarios']

if __name__=="__main__":
    from Controller.productoController import *
    from Controller.usuarioController import * 
    
    app.run(port=4004,debug=True)
    
    