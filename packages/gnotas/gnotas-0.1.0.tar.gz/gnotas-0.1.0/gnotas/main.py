#!/usr/bin/env python3

import os
from gestor import Gestor
if __name__ == '__main__':


    gestor = Gestor()
    while True:
    
        print("____________________MENU____________________")
        print("1. Añadir una nota")
        print("2. Leer una nota")
        print("3. Buscar una nota")
        print("4. Borrar una nota")
        print("5. Salir")

        opcion = input("Selecciona una opcion ")

        if opcion == "1":
            contenido = input("\n [+] Nota: ")
            gestor.agregar_notas(contenido)

        elif opcion == "2":
            notas = gestor.leer_notas()
            print("[+] Mostrando las notas:\n")
            for i, nota in enumerate(notas):
                print(f"{i+1}: {nota}")

        elif opcion == "3":
            busqueda = input("Que quieres buscar? ")
            notas = gestor.buscar_nota(busqueda)

            print("[+] Mostrando notas que coinciden: ")
            for i, nota in enumerate(notas):
                print(f"{i+1}: {nota}")

        elif opcion == "4":
            index = int(input("Cual nota quieres eliminar? "))
            gestor.eliminar_nota(index)
                 


        elif opcion == "5":
            break

        else:
            print("[!] La opcion marcada no es valida")


        input("Presione <<Enter>> para continuar...")

        os.system('cls' if os.name == 'nt' else 'clear')
