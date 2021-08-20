from filmweb.main import *

logo = ("""
     .:--==--::     
  .-=-:.:=======-.  
 :===.   ===: .-==: 
:=====---====-  -==:
==:   ==-..:==- .===
==-..:==-::-==- .===
:=====::-====-  ===:  ___ _ _                 _      _____        _    
 :===.   ===: :===-  | __(_| |_ ____ __ _____| |__  |_   ____ ___| |___
  .=+=--=++++=++=.   | _|| | | '  \ V  V / -_| '_ \   | |/ _ / _ | (_-<
    .:-==++==-:.     |_| |_|_|_|_|_\_/\_/\___|_.__/   |_|\___\___|_/__/
""")

def menu():
    print("[yellow]" + logo + "[/yellow]")
    print("1 [bold white]Export movies to imdbCSV v3[/bold white]")
    print("2 [bold white]Txt to Filmweb[/bold white]")
    print("0 [bold white]Exit[/bold white]")
    selection = input("Ch0ice: ")
    if selection == "1":
        success = set_cookies(userVariables["token"], userVariables["session"], userVariables["username"], userVariables["password"])
        print(success)
        if success != False:
            filmweb_export(userVariables["username"])
    elif selection == "2":
        txt_to_filmweb
    else:
        print("[red]Unknown option[/red]")
menu()