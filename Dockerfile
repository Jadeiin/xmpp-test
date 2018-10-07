FROM python:3.6-alpine
WORKDIR /usr/src/xmpp-test

ADD requirements.txt xmpp-test.py ./
ADD xmpp_test xmpp_test/

RUN apk --no-cache add --update gcc linux-headers libc-dev
RUN pip install --no-cache-dir -r requirements.txt

CMD python3 xmpp-test.py -h
