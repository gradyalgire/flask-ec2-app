# flask-ec2-app
Flask EC2 WebApp

**URL:** http://ec2-3-15-146-79.us-east-2.compute.amazonaws.com

**Apache**

```
WSGIDaemonProcess flaskapp user=ubuntu group=ubuntu threads=5
WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi

<Directory /var/www/html/flaskapp>
  WSGIProcessGroup flaskapp
  WSGIApplicationGroup %{GLOBAL}
Require all granted
</Directory>
```
