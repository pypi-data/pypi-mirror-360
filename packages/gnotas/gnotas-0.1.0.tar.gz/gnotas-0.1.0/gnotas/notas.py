#!/usr/bin/env python3

class Notas:

    def __init__(self, contenido):
        self.contenido = contenido

    def __str__(self):

        return self.contenido


    def coinciden(self, busqueda):
        return busqueda in self.contenido
