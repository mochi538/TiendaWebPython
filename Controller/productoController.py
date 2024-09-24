from appWeb import app, productos
from flask import request, jsonify, redirect,render_template, session
import pymongo
import os
import pymongo.errors
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import json


def productoExiste(codigo):    
    try:
        consulta = {"codigo":codigo}    
        producto = productos.find_one(consulta)
        if(producto is not None):
            return True
        else:
            return False        
    except pymongo.errors as error:
        print(error)
        return False
    


@app.route("/listarProducto")
def inicio():
    if("user" in session):
        try:
            mensaje=""
            listaProductos = productos.find()
            print(listaProductos)
        except pymongo.errors as error:
            mensaje=str(error)
            listaProductos = []
            
        return render_template("listarProducto.html", productos=listaProductos, mensaje=mensaje)
    else:
        mensaje="Se requiere iniciar sesión"
        return render_template("frmLogin.html", mensaje=mensaje)
    
@app.route("/agregar", methods=['POST', 'GET'])
def agregar():
    if("user" in session):
        if(request.method=='POST'):
            try:
                codigo = int(request.form['txtCodigo'])          
                nombre = request.form['txtNombre']
                precio = int(request.form['txtPrecio'])
                categoria = request.form['cbCategoria']
                
                foto = request.files['fileFoto']
                nombreArchivo = secure_filename(foto.filename)
                listaNombreArchivo = nombreArchivo.rsplit(".",1)
                extension = listaNombreArchivo[1].lower()
                
                nombreFoto = f"{codigo}.{extension}"        
                producto = {
                    "codigo": codigo, "nombre": nombre, "precio": precio, 
                    "categoria": categoria, "foto": nombreFoto
                }  
                
                existe = productoExiste(codigo) 
                if (existe == False):   
                    resultado = productos.insert_one(producto)
                    
                    if(resultado.acknowledged):
                        mensaje="Producto Agregado" 
                        foto.save(os.path.join(app.config["UPLOAD_FOLDER"],nombreFoto))
                        return redirect('/listarProducto')
                    else:
                        mensaje="Error desade el método Agregar"   
                else:
                    mensaje="Ya existe un producto con ese código" 
            except pymongo.errors as error:
                mensaje=error         
            return render_template("frmAgregar.html",mensaje=mensaje, producto=producto )
        else:
            if(request.method=='GET'):
                producto=None
                return render_template("frmAgregar.html", producto=producto)
    else:
        mensaje="Debe primero ingresar con sus credenciales"
        return render_template("frmLogin.html", mensaje=mensaje) 
       
       
@app.route("/consultar/<string:id>", methods=["GET"])
def consultar(id):
    if("user" in session):
        if(request.method=='GET'):
            try:
                id=ObjectId(id)
                consulta = {"_id":id}
                producto = productos.find_one(consulta)        
                return render_template("frmActualizar.html",producto=producto)
            except pymongo.errors as error:
                mensaje=error
                return redirect("/listarProductos")
    else:
        mensaje="Requiere iniciar Sesión"
        return render_template("frmLogin.html", mensaje=mensaje)
        
        
@app.route("/actualizar",methods=["POST"])        
def actualizar():
    if("user" in session):
        try:    
            if(request.method=="POST"):
                
                codigo=int(request.form["txtCodigo"])
                nombre=request.form["txtNombre"]
                precio=int(request.form["txtPrecio"])
                categoria=request.form["cbCategoria"]   
                id=ObjectId(request.form["id"])     
                
                foto = request.files["fileFoto"]
                if(foto.filename!=""):
                    nombreArchivo = secure_filename(foto.filename)           
                    listaNombreArchivo = nombreArchivo.rsplit(".",1)
                    extension = listaNombreArchivo[1].lower()
                    nombreFoto = f"{codigo}.{extension}"      
                     
                    producto = {
                        "_id": id, "codigo":codigo,"nombre":nombre,
                        "precio":precio,"categoria":categoria,"foto": nombreFoto      
                    }
                    
                else:
                    producto = {
                        "_id":id, "codigo":codigo, "nombre":nombre,
                        "precio":precio, "categoria":categoria       
                    }                    
                recibirId = {"_id":id} 
                consulta = {"$set": producto}
                #verificar si el nuevo código ya existe de un producto diferente a sí mismo
                existe = productos.find_one({"codigo": codigo, "_id":{"$ne": id}})
                if existe:
                    mensaje="Producto ya existe con ese código"
                    return render_template("frmActualizarProducto.html", producto=producto, mensaje=mensaje)
                else:
                    resultado=productos.update_one(recibirId,consulta)
                    if(resultado.acknowledged):
                        mensaje="Producto Actualizado"    
                        if(foto.filename!=""):                  
                            foto.save(os.path.join(app.config["UPLOAD_FOLDER"],nombreFoto)) 
                        return redirect("/listarProductos")  
                        
        except pymongo.errors as error:
            mensaje=error
            return redirect("/listarProducto")
    else:
        mensaje="Requiere inciar sesión"
        return render_template("frmLogin.html", mensaje=mensaje)
    
@app.route("/eliminar/<string:id>")
def eliminar(id):
    if("user" in session):
        try:
            id = ObjectId(id)
            recibirId = {"_id":id}
            producto = productos.find_one(recibirId)
            print(producto)
            nombreFoto = producto['foto']
            resultado = productos.delete_one(recibirId)
            
            if(resultado.acknowledged):
                mensaje="Producto Eliminado"
                 
                if nombreFoto != "":
                    ruta= f'{app.config['UPLOAD_FOLDER']}/ {nombreFoto}'
                    
                    if (os.path.exists(ruta)):
                        os.remove(ruta)
                         
        except pymongo.errors as error:
            mensaje=str(error)        
        return redirect("/listarProducto") 
    else:
        mensaje="Requiere iniciar sesión"
        return render_template("frmLogin.html", mensaje=mensaje)     
        
        
"""
@app.route("/api/listarProductos",methods=["GET"])
def apiListarProductos():
    listaProductos=list(productos.find())
    lista=[]
    for p in listaProductos:       
        producto={
            "_id": str(p['_id']),
            "codigo":p['codigo'],
            "nombre": p['nombre'],
            "precio": p['precio'],
            "categoria": p['categoria'],
            "foto": p['foto']
        }
        
        lista.append(producto)        
    retorno = {'productos': lista}
    return jsonify(retorno)

@app.route("/api/consultar/<string:id>",methods=["GET"])
def apiConsultar(id):
    consulta = {"_id":ObjectId(id)}
    p = productos.find_one(consulta) 
    if p:
        producto={
            "_id": str(p['_id']),
            "codigo":p['codigo'],
            "nombre": p['nombre'],
            "precio": p['precio'],
            "categoria": p['categoria'],
            "foto": p['foto']
        }
        retornar = {'producto': producto}
    else:
        retornar = {'mensaje|':"No existe producto con ese Id"}
        
    return jsonify(retornar)
    

@app.route("/api/agregar",methods=["POST"])
def apiAgregarP():    
    try:
        producto=None
        mensaje=""
        codigo = int(request.json['codigo'])          
        nombre = request.json['nombre']
        precio = int(request.json['precio'])
        categoria = request.json['categoria']
        foto = request.json['foto']
        producto = {
                "codigo": codigo, 
                "nombre": nombre,
                "precio": precio, 
                "categoria": categoria,
                "foto": foto
        }  
        existe = productoExiste(codigo)
        
        if not existe:   
            resultado = productos.insert_one(producto)
            if resultado.acknowledged:
                mensaje= "Producto Agregado"                
            else:
                mensaje="Error desde el método apiAgregarP"   
        else:
            mensaje=f"Ya existe un producto con el código {codigo}" 
            
    except pymongo.errors.PyMongoError as error:
        mensaje = str(error)
    
  
    returnar = {"mensaje":mensaje}
    return jsonify(returnar)
"""