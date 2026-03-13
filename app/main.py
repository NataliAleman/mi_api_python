from flask import Flask, request, jsonify
import mysql.connector
import json 
import serial

ser = serial.Serial('COM3', 115200)

while True:
    linea = ser.readline().decode().strip()

    try:
        data = json.loads(linea)
        uid = data["uid"]
        print("Tarjeta:", uid)

    except:
        pass