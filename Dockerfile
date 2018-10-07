FROM python:3.6-alpine
WORKDIR /usr/src/xmpp-test

ADD requirements.txt .
ADD xmpp-test.py .
ADD xmpp_test xmpp_test/
RUN pip install -U pip setuptools && pip install -r requirements.txt

CMD python xmpp-test.py -h
