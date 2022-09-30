FROM odoo:13.0

USER root

RUN apt-get update

RUN apt-get install python3 \
    python-dev \
    python3-dev \
    build-essential libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev zlib1g-dev \
    python-pip \
    python3-venv \
    python3-wheel -y

RUN apt-get update -y

RUN apt-get install -y tesseract-ocr-eng \
    phantomjs \
    pkg-config \
    build-essential \
    libtesseract-dev \
    tesseract-ocr \
    libssl-dev \
    libffi-dev \
    python-dev \
    xmlsec1 \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    libxml2 \
    wget \
    nano \
    tar \
    libxslt-dev

RUN pip3 install pkgconfig \
    && pip3 install xmlsec==1.3.3 \
    && pip3 install pytesseract==0.3.3 \
    && pip3 install json2xml==3.0.1 \
    && pip3 install lxml==4.5.0 \
    && pip3 install qrcode \
    && pip3 install python-barcode \
    && pip3 install num2words \
    && pip3 install bs4 \
    && pip3 install sunatservice==1.0.133 \
    && pip3 install dict2xml==1.5 \
    && pip3 install python-dateutil \
    && pip3 install psycopg2 \
    && pip3 install babel \
    && pip3 install PyPDF2 \
    && pip3 install passlib \
    && pip3 install  werkzeug==0.14.1 \
    && pip3 install decorator \
    && pip3 install psutil \
    && pip3 install jinja2 \
    && pip3 install reportlab \
    && pip3 install jsonschema \
    && pip3 install watchdog \
    && pip3 install psutil

COPY ./ /

RUN  chown -R 777  /var/lib/odoo

RUN  chown -R odoo  /13.0

USER odoo

RUN odoo --stop-after-init --dev=reload
