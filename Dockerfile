FROM arm32v7/python:3.8-slim-buster

#FROM python:3.8-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /
COPY mfm2mqtt.py /
# RUN pip3 uninstall serial 
# RUN python3 -m pip3 install pyserial
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "python3", "./mfm2mqtt.py" ]