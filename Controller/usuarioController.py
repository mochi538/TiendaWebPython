from appWeb import app, usuarios
from flask import render_template, request, redirect, session
import yagmail
import threading


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("frmLogin.html")
    else:
        if request.method == 'POST':
            username = request.form['txtUsername']
            password = request.form['txtPassword']
            usuario = {
                "username":username,
                "password":password
            }
            existeUser = usuarios.find_one(usuario)
            if(existeUser):
            
                session['user']=usuarios  
                email = yagmail.SMTP("mariar53804@gmail.com", open(".password").read(),
                                encoding='UTF-8')
                asunto="Reporte ingreso al sistema usuario"
                mensaje = f"Te están hakeando muak"
                
                          
                thread = threading.Thread( target=enviarCorreo, 
                    args=(email,"mariar53804@gmail.com",asunto, mensaje ))
                thread.start()
                return redirect("/listarProducto")
            else:
                mensaje="Credenciales de ingreso ivalidas"
                return render_template("frmLogin.html",mensaje=mensaje)
            
@app.route("/salir")
def salir():
    session.pop('user', None)
    session.clear()
    return render_template("frmLogin.html",mensaje="Se cerró la sesión")


def enviarCorreo(email=None, destinatario=None, asunto=None, mensaje=None):
    email.send(to=destinatario, subject=asunto, contents=mensaje)