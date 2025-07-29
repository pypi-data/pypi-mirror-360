# GambozinoHunter

## Intro

GambozinoHunter is a cli tool for network scanning and vulnerability scanning.

## To run the project

First you have to install python in your machine.

After that you need to run this inside the project:

```bash
python -m venv .venv

# For linux/mac
source .venv/bin/activate

# For Windows
.venv\Scripts\activate.bat

# Install requirements
pip install -r requirents.txt
```

## Description of the project

É necessário,ao longo das aulas, elaborar e desenvolver um script central de apoio à recolha de informação e elaboração de um relatório, denominado “o mapa da Mina” ​ (Trabalho 2)

Bom dia, venho por este meio descrever o trabalho 2, baseado na matéria dada em Python, do qual têm 3 partes:

Parte 1:
(class networkScanner())
Efectuar um código que recebe dados, baseados em IP's, input -> validar input
Pode set o primeiro e último IP que pretendem, uma rede ou várias redes, fica ao vosso critério, basta um destes dados.
E efectua um rastreio da rede, via ligação fisica ou wifi, e identifica que IP's estão activos.

Parte 2:
Com base na lista de IP's identificados como activos, parte 1, efectua uma identificação e caracterização das máquinas, como identificação dos portos disponiveis, o sistema operativo, aplicações, versões, dos serviços identificados serviços.

Parte 3:
Com base nos dados recolhidos na parte 1 e 2, escrever num ficheiro ou vários e mostrar o output, o que vos beneficiar mais, os resultados, de preferência, se conseguirem, ordenar os dados por IP ou tipo de aplicações.
Esta parte é mais criativa, podem desenvolver a ordenação e output ou nos fcheiros, como preferirem.

# TODO LIST

- [ ] Validação de IPs, Range de IPs, Network, etc...
- [ ] Scan Ports a partir de IP retornar IPs ativos e respectivos ports
- [ ]

## Prova de Conceito nº1

```python
vulnerability.py

#!/usr/bin/python3

import socket
import os
import sys
from termcolor import colored, cprint


def retBanner(ip, port):
    try:
        socket.setdefaulttimeout(2)
        sock = socket.socket()
        sock.connect((ip, port))
        banner = sock.recv(1024)
        banner = banner.decode()
        return banner
    except:
        return


def checkVulns(banner, filename):
    f = open(filename, "r")
    for line in f.readlines():
        if line in banner:
            print(colored('[+] Server is vulnerable: ' + banner, 'red'))


def main():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print('[-] File Doesnt Exist!')
            exit(0)
        if not os.access(filename, os.R_OK):
            print('[-] access Denied!')
            exit(0)
    else:
        print('[-] Usage: ' + str(sys.argv[0]) + ' <vuln filename > ')
        exit(0)
    portlist = [21, 22, 25, 80, 110, 443, 445]
    for x in range(8, 15):
        ip = '10.0.97.' + str(x)
        for port in portlist:
            banner = retBanner(ip, port)
            if banner:
                cprint('[+] ' + ip + '/' + str(port) + ': ' + banner.strip("\n"), 'cyan', 'on_grey')
                checkVulns(banner, filename)


if _name_ == '_main_':
    main()
```

## Prova de Conceito nº2

```python
portscanner.py

import socket
from IPy import IP

class portscan():
    banners = []
    open_ports = []

    def _init_(self, target, port_num):
        self.target = target
        self.port_num = port_num

    def scan(self):
        for port in range(1, self.port_num):
            self.scan_port(port)


    def check_ip(self):
        try:
            IP(self.target)
            return(self.target)
        except ValueError:
            return socket.gethostbyname(self.target)


    def scan_port(self, port):
        try:
            converted_ip = self.check_ip()
            sock = socket.socket()
            sock.settimeout(0.5)
            sock.connect((converted_ip, port))
            self.open_ports.append(port)
            try:
                banner = sock.recv(1024).decode().strip('\n').strip('\r')
                self.banners.append(banner)
            except:
                self.banners.append(' ')
            sock.close()
        except:
            pass
```
