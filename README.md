# Snake-Ping

## Work in Progress

Tested on Ubuntu 20.04 with crapd

**Dependencies**<br />
Python 3.7 or higher<br />
```
pip3 install bs4 pyppeteer
apt-get -y install chromium-browser
```

**Known Bugs**<br />
- May crash sometimes (fill a tiket, if it does)
- Country Mapping may break depending on Plugin and Country

**Examples**<br />

To Ping from all Nodes located in the Netherlands
```
python3 snake.py NL 1.1.1.1
```

To find the lowest route in-between 2 Servers in 2 different countries
```
python3 snake.py UK,NL compare
```