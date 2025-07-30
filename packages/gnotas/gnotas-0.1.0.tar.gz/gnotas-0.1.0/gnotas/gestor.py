#!/usr/bin/env python3

import pickle
from notas import Notas
class Gestor:

    def __init__(self, archivo='notas.pkl'):
        self.archivo = archivo


        try:
            with open(self.archivo, 'rb') as f:
                self.notas = pickle.load(f)
        except FileNotFoundError:
            self.notas = []

    def guardar_notas(self):
        with open(self.archivo, 'wb') as f:
            pickle.dump(self.notas, f)

    def agregar_notas(self, contenido):
        self.notas.append(Notas(contenido))
        self.guardar_notas()

    def leer_notas(self):
        return self.notas

    def buscar_nota(self, busqueda):
        return [nota for nota in self.notas if nota.coinciden(busqueda)]

    def eliminar_nota(self, index):
        if index < len(self.notas):
            del self.notas[index]
            self.guardar_notas()


    
