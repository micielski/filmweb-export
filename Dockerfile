FROM selenium/standalone-firefox
WORKDIR /filmweb-export
COPY . .
RUN sudo chown -R seluser: .
RUN sudo apt update && sudo apt install -y python3 python3-pip
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "filmweb.py" ]
