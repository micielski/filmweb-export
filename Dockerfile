FROM selenium/standalone-firefox
WORKDIR /filmweb-export
COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD [ "filmweb.py" ]
