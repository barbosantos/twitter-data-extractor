FROM python:3.6

COPY requirements.txt /tmp/requirements.txt
RUN pip install -q --upgrade pip \
    && pip install -q -r /tmp/requirements.txt\
    && rm /tmp/requirements.txt

COPY *.py ./
RUN /bin/bash -c 'ls -la; chmod +x ./*.py; ls -la'

ENTRYPOINT [ "sh" ]