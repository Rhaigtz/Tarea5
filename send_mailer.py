import yagmail

html = open('index.html', 'r')

yagmail.SMTP({"correo@dominio": "noreply@steampowered.com"}, "pwd").send(
    'correo@target_dominio', 'Steam Support <notreply@steampowered.com>', html.read().replace('\n', ''))

html.close()
