import time
import json
import threading
import os
import subprocess
import sys
import pprint

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import smtplib
from email.mime.text import MIMEText

import nmap
from socket import inet_aton
pp = pprint.PrettyPrinter(indent=4)


class NetworkScanner():

    def __init__(self, jsonfile, logfile):
        # Global Variables
        self.jsonfile = jsonfile
        self.logfile = logfile
        self.settings = self.ReadSettings()
        self.devices = []
        self.rerun = False

        # Init Scanner
        self.writeLog("Scanner App Booted")
        self.nm = nmap.PortScanner()
        # self.startScanning()

    def runForever(self):
        self.rerun = True
        threading.Thread(target=self.startScanning).start()

    def startScanning(self):
        print "startScanning..."
        self.nm.scan(hosts=self.settings['options']['hosts'], arguments='-sP -n')
        self.settings = self.ReadSettings()
        savedDevices = self.settings["devices"]
        foundNewDevice = False
        self.devices = []
        for host in self.nm.all_hosts():
            if 'mac' in self.nm[host]['addresses']:
                newMac = self.nm[host]['addresses']['mac']
                hostState = self.nm[host]['status']['state']
                if newMac not in savedDevices:
                    foundNewDevice = True
                    hostStatus = "new"
                    if newMac in self.nm[host]['vendor']:
                        hostName = self.nm[host]['vendor'][newMac]
                    else:
                        hostName = "unknown"
                else:
                    hostStatus = "known"
                    hostName = savedDevices[newMac]['name']
                self.devices.append({
                    "ip": host,
                    "mac": newMac,
                    "status": hostStatus,
                    "state": hostState,
                    "name": hostName
                })
            else:
                # self.nm[host]['status']['reason'] == localhost-response
                self.writeLog("Error with this IP: {ip}".format(ip=host))

        # Add Known Offline Devices
        for oldMac in savedDevices:
            foundMac = False
            for device in self.devices:
                if oldMac == device['mac']:
                    foundMac = True
            if foundMac is False:
                self.devices.append({
                    "ip": savedDevices[oldMac]['ip'],
                    "mac": oldMac,
                    "status": "known",
                    "state": "down",
                    "name": savedDevices[oldMac]['name']
                })

        self.devices = sorted(self.devices, key=lambda item: inet_aton(item['ip']))

        if foundNewDevice:
            self.newDeviceDetected()

        if self.rerun is True:
            threading.Timer(5, self.startScanning).start()

    def newDeviceDetected(self):
        self.writeNewDevices()
        mailBody = "\nNew device has been detected.\n\n"
        for device in self.devices:
            if device['status'] == 'new':
                mailBody = mailBody + "Device: {mac}\nIP: {ip}\nName: {name}\n\n".format(**device)
                self.writeLog("new divice with MAC: {mac}".format(**device))
        self.sendMail(mailBody)

    def writeNewDevices(self):
        settingsDevices = {}
        for device in self.devices:
            settingsDevices[device['mac']] = {
                "ip": device['ip'],
                "name": device['name']
            }
        self.settings['devices'] = settingsDevices

        with open(self.jsonfile, 'w') as outfile:
            json.dump(self.settings, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        socketio.emit('refresh_devices', self.getDevices())

    def ReadSettings(self):
        with open(self.jsonfile) as data_file:
            settings = json.load(data_file)
        return settings

    def writeLog(self, message):
        myTimeLog = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        with open(self.logfile, "a") as myfile:
            myfile.write(myTimeLog + message + "\n")

    def sendMail(self, myBodyMessage):
        if self.settings['mail']['enable'] is True:
            mail_user = self.settings['mail']['username']
            mail_pwd = self.settings['mail']['password']
            smtp_server = self.settings['mail']['smtpServer']
            smtp_port = self.settings['mail']['smtpPort']

            msg = MIMEText(myBodyMessage)
            sender = mail_user
            recipients = self.settings['mail']['recipients']
            msg['Subject'] = self.settings['mail']['messageSubject']
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)

            smtpserver = smtplib.SMTP(smtp_server, smtp_port)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.login(mail_user, mail_pwd)
            smtpserver.sendmail(sender, recipients, msg.as_string())
            smtpserver.close()

    def changeName(self, mac, name):
        for i, device in enumerate(self.devices):
            if device['mac'] == mac:
                self.devices[i]['name'] = name
        self.writeNewDevices()

    def refreshDevices(self):
        self.startScanning()
        socketio.emit('refresh_devices', self.getDevices())

    def getDevices(self):
        return sorted(self.devices, key=lambda k: k['name'])


app = Flask(__name__, static_url_path='')
socketio = SocketIO(app)
wd = os.path.dirname(os.path.realpath(__file__))
webDirectory = os.path.join(wd, 'web')
jsonfile = os.path.join(wd, "settings.json")
logfile = os.path.join(wd, "alert.log")
sipcallfile = os.path.join(wd, "voip")
scanner = NetworkScanner(jsonfile, logfile)
# scanner.startScanning()
scanner.runForever()


@app.route('/')
def index():
    return send_from_directory(webDirectory, 'index.html')


@app.route('/main.css')
def main():
    return send_from_directory(webDirectory, 'main.css')


@app.route('/icon.png')
def icon():
    return send_from_directory(webDirectory, 'icon.png')


@app.route('/mycss.css')
def mycss():
    return send_from_directory(webDirectory, 'mycss.css')


@app.route('/mycssMobile.css')
def mycssMobile():
    return send_from_directory(webDirectory, 'mycssMobile.css')


@app.route('/myjs.js')
def myjs():
    return send_from_directory(webDirectory, 'myjs.js')


@app.route('/getDevices.json')
def getDevices():
    return json.dumps(scanner.getDevices())


@socketio.on('changeName')
def changeName(message):
    print(message)
    scanner.changeName(message['mac'], message['name'])
    socketio.emit('pinsChanged')

if __name__ == '__main__':
    socketio.run(app, host="", port=5000)
