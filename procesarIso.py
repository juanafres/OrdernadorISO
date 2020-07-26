import sys
import os
import json
import time
import shutil

from tkinter import *    # Carga módulo tk (widgets estándar)
from tkinter import ttk  # Carga ttk (para widgets nuevos 8.5+)
import tkinter as tk

def leerJson(ruta):
	operaciones = json.loads(open(ruta).read())
	dictOperaciones = {}
	for i in range(len(operaciones["operaciones"])):
		if operaciones["operaciones"][i]["activo"] == "S":
			dictOperaciones[operaciones["operaciones"][i]["codOp"]] = operaciones["operaciones"][i]["nombre"]
	return dictOperaciones
		
def desplegarHexa(caract):
	if (caract == '0' ): return "0000" 
	if (caract == '1' ): return "0001"
	if (caract == '2' ): return "0010"
	if (caract == '3' ): return "0011"
	if (caract == '4' ): return "0100"
	if (caract == '5' ): return "0101"
	if (caract == '6' ): return "0110"
	if (caract == '7' ): return "0111"
	if (caract == '8' ): return "1000"
	if (caract == '9' ): return "1001"
	if (caract == 'A' ): return "1010"
	if (caract == 'B' ): return "1011"
	if (caract == 'C' ): return "1100"
	if (caract == 'D' ): return "1101"
	if (caract == 'E' ): return "1110"
	if (caract == 'F' ): return "1111"
	return False

def esLink(iso):
	primerElemPrimaryBitmap = iso[16]
	map = desplegarHexa(primerElemPrimaryBitmap) 
	if map[1] == '1':
		return False #es banelco
	else: return True
	
def codOPLink(iso):
	return iso[48:50] # es link
	
def darIso(tira):
	n = tira.find("ISO")
	if n < 0:	
		return ""
	else:
		return tira[n:]
		
def esTrk(nombreArchivo):
	punto = nombreArchivo[-4:-3]
	terminacion = nombreArchivo[-3:].lower()
	if terminacion == "trk" and punto == ".":
		return True
	else:
		return False
		
def procesaArchivo(archivo, ruta, dicOp):
	opAlineadas = {}
	rutaComp = ruta + "\\" + archivo
	arch = open(rutaComp)
	for linea in arch.readlines():
		iso = darIso(linea)
		if (not iso == ""):
			if (esLink(iso)):
				codOp = codOPLink(iso)
				if codOp in dicOp:
					nom = dicOp[codOp]
				else:
					if "00" in dicOp:
						nom = dicOp["00"]
					else: 
						nom = "Default"		
				if nom in opAlineadas:
					isos = opAlineadas[nom]
					isos.append(iso)
					opAlineadas[nom] = isos
				else:
					isos = []
					isos.append(iso)
					opAlineadas[nom] = isos	
	arch.close()
	return opAlineadas
	
def recorrerEscritorio(directorio,dicOp):
	todasOp = {}
	vectDic = []
	contenidoDir = os.listdir(directorio)
	for archivo in contenidoDir:
		if esTrk(archivo):
			vectDic.append( procesaArchivo(archivo,directorio,dicOp))	
	return vectDic
			
def armarDiccionario(vectDic):
	completo = {}
	for dic in vectDic:
		vals = dic.keys()
		if (len(vals) > 0):
			for valor in vals:
				if valor in completo:
					isos = completo[valor]					
					for iso in dic[valor]:
						isos.append(iso)
					completo[valor] = isos
				else:
					completo[valor] = dic[valor]	
	return completo

def armarEscritorio(dic,ruta):
	rutaTemp = ruta + "\\temp"
	if not os.path.exists(rutaTemp):
		os.mkdir(rutaTemp)
	else:
		shutil.rmtree(rutaTemp)
		time.sleep(2)
		os.mkdir(rutaTemp)
	nombreOp = dic.keys()
	for nom in nombreOp:
		file = open(rutaTemp + "\\" + nom + ".trk",'w') 
		isos = dic[nom]
		for iso in isos:
			file.write(iso) 		 
		file.close() 

def onArmarDir():

	directorio = entradaDir.get()
	entradaDir.delete(0, END)
	rutaOp = entradaOp.get()
	entradaOp.delete(0, END)
	
	directorio.replace('\\','\\\\')
	rutaOp.replace('\\','\\\\')
	
	if not os.path.exists(rutaOp):
		win = tk.Toplevel()
		win.wm_title("Error")
		Label(win, text="No existe el archivo config, por favor creelo", height=3, width=50).pack()
		ok = Button(win, text="OK", command=win.destroy)
		ok.pack()
		ok.bind("<Return>", lambda a: win.destroy())
		ok.focus_set()

	else:
		op = leerJson(rutaOp)
		if not os.path.exists(directorio):
			win = tk.Toplevel()
			win.wm_title("Error")
			Label(win, text="directorio de trks", height=3, width=50).pack()
			ok = Button(win, text="OK", command=win.destroy)
			ok.pack()
			ok.bind("<Return>", lambda a: win.destroy())
			ok.focus_set()
		else:
			armarEscritorio(armarDiccionario(recorrerEscritorio(directorio,op)),directorio)

def onArmarConfig():
	entradaDir.delete(0, END)
	rutaOp = entradaOp.get()
	entradaOp.delete(0, END)
	rutaOp.replace('\\','\\\\')
	#+ "\\config.json"
	file = open(rutaOp,'w') 
	file.write("""{
    "operaciones": 
	[
		{"codOp": "00", "nombre": "Otras"		 , "activo":"S"	},
		{"codOp": "01", "nombre": "Extraccion"   , "activo":"S" },
		{"codOp": "F4", "nombre": "DebinDebito"  , "activo":"S" },
		{"codOp": "F3", "nombre": "DebinCredito" , "activo":"S" }
    ]
}""") 
	file.close()
	
raiz = Tk()
raiz.geometry('600x200')
raiz.configure(bg = 'beige')
raiz.title('Separador TRK')

ttk.Button(raiz, text='Salir', command=quit).pack(side=BOTTOM)

texto1 = Text(raiz, height=1, width=60)
texto1.pack()
texto1.insert(END, "Inserte la ruta del directorio trks")
texto1.config(state=DISABLED)

entradaDir = Entry(raiz, width=60)
entradaDir.pack()
entradaDir.insert(0, "e:\\JuanF\\Desktop\\prueba")

texto2 = Text(raiz, height=1, width=60)
texto2.pack()
texto2.insert(END, "Inserte ruta del archivo de config")
texto2.config(state=DISABLED)

entradaOp = Entry(raiz, width=60)
entradaOp.pack()
entradaOp.insert(0, "e:\\JuanF\\Desktop\\config.json")

ttk.Button(raiz, text='Crear config', command=onArmarConfig).pack(side=BOTTOM)
ttk.Button(raiz, text='Crear directorio', command=onArmarDir).pack(side=BOTTOM)

raiz.mainloop()

