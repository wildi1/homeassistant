ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

COPY requirements.txt /requirements.txt

RUN apk add --update --no-cache curl jq python3 git &&  pip3 install --no-cache-dir -r "/requirements.txt"

# Copy data for add-on
COPY run.sh /
COPY mqtt_echo.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]