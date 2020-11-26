import time
from itertools import chain
import email
import imaplib
import re

imap_ssl_host = 'imap.gmail.com'  # imap.mail.yahoo.com
imap_ssl_port = 993
username = ''
password = ''


criteria = []
criteria_check = []
uid_max = 0

regexFile = open('regex.txt', 'r')
line_counter = 0

# Genera el arreglo criteria para el criterio de busqueda de imap y criteria_check para verificar el id con el respectivo regex
for regex in regexFile:
    line_counter = line_counter + 1
    sender = regex.split(';')
    criteria.append({
        'FROM': sender[0],
    })
    criteria_check.append({
        'FROM': sender[0],
        'REGEX': sender[1],
        'DATE': sender[2]
    })

regexFile.close()

#  Transforma el arreglo en el formato que lo recibe la query de imap


def search_string(uid_max, criteria):
    c = []
    counter = 1
    for i in criteria:
        criteria_list = list(map(lambda t: (t[0], '"'+str(t[1])+'"'),
                                 i.items()))
        if counter == line_counter:
            criteria_list = criteria_list + [('UID', '%d:*' % (uid_max+1))]
        else:
            criteria_list = [('OR',)] + criteria_list
        c.extend(criteria_list)
        counter = counter + 1
    return '(%s)' % ' '.join(chain(*c))


# Inicio de sesión y escucha de los correos en INBOX
server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
server.login(username, password)
server.select('INBOX')

result, data = server.uid('search', None, search_string(uid_max, criteria))

# Identificador del mensaje en el correo, solo seran escuchados mensajes entrantes.

uids = [int(s) for s in data[0].split()]
if uids:
    uid_max = max(uids)

server.logout()

# Conecto y reconecto para volver a cargar los nuevos mensajes.
while 1:

    # Vuelvo a iniciar la instancia de servidor ya que sino tira un error.
    server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    server.login(username, password)
    server.select('INBOX')

    result, data = server.uid('search', None, search_string(uid_max, criteria))
    uids = [int(s) for s in data[0].split()]
    for uid in uids:

        # Compruebo que el uid correponda a los ultimos.
        if uid > uid_max:
            result, data = server.uid(
                'fetch', str(uid), '(RFC822)')
            msg = email.message_from_string(data[0][1].decode())
            msg_id = msg.get('Message-ID').replace('<', '').replace('>', '')

            email_subject = msg['subject']
            email_from = msg['from']

            print('Subject: ', email_subject, '\n')
            print('Enviado por: ', email_from, '\n')

            for element in criteria_check:
                print(msg_id)
                from_email = re.search(element['FROM'], email_from)

                if from_email:

                    matched = re.match(
                        element['REGEX'].replace('\n', ''), msg_id)
                    is_match = bool(matched)
                    if not is_match:
                        print(
                            'Correo posiblemente falso, revisar regex ya que su validez es desde el: ', element['DATE'], '\n')
                    else:
                        print(
                            'Correo probablemente original segun criterio de regex.\n')

            uid_max = uid

            print('Nuevo mensaje -------------------------\n')

    server.logout()
time.sleep(1)
