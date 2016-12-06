# Network Scanner

This application scans the network and sends an email when a new device is detected.

## Installation
```
cd /opt/
sudo git clone https://github.com/bkbilly/network_scanner.git
cd /opt/network_scanner/
sudo cp /opt/network_scanner/settings_template.json /opt/network_scanner/settings.json
sudo pip install -r opt/network_scanner/requirements.txt
sudo chmod +x /opt/network_scanner/networkscanner
sudo ln -s /opt/network_scanner/networkscanner /etc/init.d/networkscanner
sudo update-rc.d networkscanner defaults
sudo service networkscanner start
```

## How to use settings.json

* `mail.enable` (bool) Enable email alerts
* `mail.username` (str) Username of your mail
* `mail.password` (str) Password of your mail
* `mail.smtpServer` (str) SMTP of your mail
* `mail.smtpPort` (int) SMTP Port of your mail
* `mail.recipients` (list str) List of recipents. eg. ["mail1@example.com", "mail2@example.com"]
* `mail.messageSubject` (str) Subject of the sent mail
* `options.hosts` (str) Network to scan in CIDR format
* `options.scanInterval` (int) Set the scan interval in seconds
* `options.orderBy` (str) For the UI, order hosts by name or ip

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
