from python:3.7

# RUN apt-get update  && apt-get install -y \
#     libsasl2-dev unixodbc-dev cron

ADD ./requirements-dev.txt .
RUN pip3 install --trusted-host pypi.python.org \
    pytest \
    twine

ENTRYPOINT [ "/bin/sh" ]