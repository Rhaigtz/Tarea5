import yagmail
yagmail.SMTP({"correo": "noreply@steampowered.com"}, "pwd").send(
    'correo', 'titulo del mensaje', 'mucho texto mucho texto')
