FROM selenium/standalone-firefox
WORKDIR /home/seluser/
COPY . /home/seluser
RUN sudo chown -R seluser: .
RUN sudo apt update && sudo apt install -y python3 python3-pip
RUN pip install --no-cache-dir -r /home/seluser/requirements.txt
USER seluser
ENV DOCKER Yes

ENTRYPOINT [ "python3", "export.py" ]
