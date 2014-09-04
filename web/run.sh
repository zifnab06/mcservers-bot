sudo -u www-data uwsgi -s /tmp/mcservers.sock --module app --callable app 2>&1 | sudo -u www-data tee /var/log/mcservers.log >/dev/null & 
