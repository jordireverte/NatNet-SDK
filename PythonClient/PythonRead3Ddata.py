import sys
import time
import os
from NatNetClient import NatNetClient

# Diccionari global per guardar la posició de TOTS els objectes
# Clau: ID de l'objecte, Valor: [posició, rotació]
rigid_bodies_data = {}

def receive_rigid_body_frame(new_id, position, rotation):
    """Callback que s'executa per cada objecte en cada frame."""
    global rigid_bodies_data
    rigid_bodies_data[new_id] = [position, rotation]

def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len = len(arg_list)
    if arg_list_len > 1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len > 2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len > 3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False
        if arg_list_len > 4:
            args_dict["stream_type"] = arg_list[4]
    return args_dict

if __name__ == "__main__":

    # Reestablim els valors
    id_body = 0
    pos = [0,0,0]
    rot = [0,0,0,1] 

    optionsDict = {}
    optionsDict["clientAddress"] = "127.0.0.1"
    optionsDict["serverAddress"] = "127.0.0.1"
    optionsDict["use_multicast"] = None
    optionsDict["stream_type"] = None
    stream_type_arg = None

    # Creacio client NatNet
    optionsDict = my_parse_args(sys.argv, optionsDict)
    streaming_client = NatNetClient()
    streaming_client.set_client_address(optionsDict["clientAddress"])
    streaming_client.set_server_address(optionsDict["serverAddress"])


    print("--- OptiTrack NatNet Minimal Receiver ---")

    # 1. Selecció Multicast o Unicast
    cast_choice = input("Select 0 for multicast and 1 for unicast: ")
    cast_choice = int(cast_choice)
    while cast_choice != 0 and cast_choice != 1:
        cast_choice = input("Invalid option. Select 0 for multicast or 1 for unicast: ") #type: ignore  # noqa F501
        cast_choice = int(cast_choice)
        
    if cast_choice == 0:
        optionsDict["use_multicast"] = True
    else:
        optionsDict["use_multicast"] = False
    streaming_client.set_use_multicast(optionsDict["use_multicast"])

    # 2. Direccions IP
    client_ip = input("IP del Client (deixa buit per 127.0.0.1): ") or "127.0.0.1"
    server_ip = input("IP del Servidor Motive (deixa buit per 127.0.0.1): ") or "127.0.0.1"
    
    streaming_client.set_client_address(client_ip)
    streaming_client.set_server_address(server_ip)

    # 3. Configuració de Listeners (Només el de Rigid Bodies)
    streaming_client.rigid_body_listener = receive_rigid_body_frame
    streaming_client.set_print_level(0)
    # 4. Iniciar el client en mode 'd' (Data Stream)
    if not streaming_client.run("d"):
        print("ERROR: No s'ha pogut iniciar el client.")
        sys.exit(1)

    time.sleep(1)
    if not streaming_client.connected():
        print("ERROR: No s'ha pogut connectar. Revisa el streaming de Motive.")
        sys.exit(2)

    print("\nConnexió establerta. Mostrant dades cada segon...")
    print("Prem Ctrl+C per aturar.\n")

    try:
        ID_REFERENCIA = 1  # L'ID que vols que sigui el 0,0,0

        while True:
            if not rigid_bodies_data:
                print("Esperant dades dels objectes...", end="\r")
            elif ID_REFERENCIA not in rigid_bodies_data:
                print(f"Error: Referència (ID 1) no trobada.", end="\r")
            else:
                # 1. Obtenim la posició de la referència per fer el càlcul
                p_ref = rigid_bodies_data[ID_REFERENCIA][0]
                
                output_total = "" # Variable per acumular les línies
                
                # 2. Recorrem TOTS els cossos rígids
                for body_id, data in rigid_bodies_data.items():
                    p_glob = data[0] # Posició global de Motive
                    r = data[1]      # Rotació (quaternions)
                    
                    # 3. FEM LA RESTA: Posició relativa
                    p_rel = [
                        p_glob[0] - p_ref[0],
                        p_glob[1] - p_ref[1],
                        p_glob[2] - p_ref[2]
                    ]
                    
                    # 4. Afegim la línia a l'output (la REF sortirà 0,0,0 automàticament)
                    etiqueta = "REF" if body_id == ID_REFERENCIA else "TRA"
                    output_total += (f"{etiqueta} (ID {body_id:2}): Pos[{p_rel[0]:6.3f}, {p_rel[1]:6.3f}, {p_rel[2]:6.3f}] | "
                                     f"Rot[{r[0]:6.3f}x, {r[1]:6.3f}y, {r[2]:6.3f}z, {r[3]:6.3f}w]\n")

                # 5. Netegem i imprimim tot el bloc d'un sol cop
                os.system('cls' if os.name == 'nt' else 'clear')
                print(output_total, end="")
            
            time.sleep(1/120)

    except KeyboardInterrupt:
        print("\nAturant el programa...")