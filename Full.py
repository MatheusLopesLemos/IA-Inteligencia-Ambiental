import mysql.connector
from tkinter import messagebox, filedialog, ttk
import tkinter as tk
import cv2
import os
from datetime import date
from tensorflow import keras

# Variáveis globais
contador_tem_animal = 0
contador_imagens = 0
model = keras.models.load_model("model1.keras")

# Função para conectar com Banco de Dados
def conectar_db():
    try:
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='',
            database='projeto_guapiacu'
        )
        return con
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para consultar o ID do funcionário
def consultar_id_funcionario(user, cursor):
    query = "SELECT id_funcionario FROM funcionario WHERE nome = %s"
    cursor.execute(query, (user,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Assume-se que o nome de funcionário é único
    else:
        raise ValueError(f"Funcionário com o nome {user} não encontrado.")

# Função para consultar o ID da câmera
def consultar_id_camera(camera, cursor):
    query = "SELECT id_camera FROM camera WHERE nome_camera = %s"
    cursor.execute(query, (camera,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Assume-se que o nome de câmera é único
    else:
        raise ValueError(f"Câmera com o nome {camera} não encontrada.")

# Função para selecionar uma pasta
def selecionar_pasta():
    caminho_selecionado = filedialog.askdirectory()
    return caminho_selecionado

# Função para criar uma pasta
def criar_pasta(destino):
    try:
        if not os.path.exists(destino):
            os.makedirs(destino)
            print(f"Pasta criada com sucesso!")
        else:
            print(f"A pasta '{destino}' já existe.")
    except Exception as e:
        print(f"Erro ao criar a pasta: {e}")

# Função de execução
def execucao(destino_dir, camera, user):
    # Conectar ao banco de dados
    con = conectar_db()
    if con:
        try:
            cursor = con.cursor()

            global contador_tem_animal, contador_imagens
            contador_tem_animal = 0
            contador_imagens = 0

            destino_dir_convertida = destino_dir.replace('/', '\\')
            pasta_tem_animal = f'{destino_dir_convertida}\\COM ANIMAL'
            pasta_nao_animal = f'{destino_dir_convertida}\\SEM ANIMAL'

            criar_pasta(pasta_tem_animal)
            criar_pasta(pasta_nao_animal)

            extensoes_validas = ('.jpg', '.png', '.jpeg')

            if destino_dir_convertida:
                arquivos_na_pasta = os.listdir(destino_dir_convertida)

                for arquivo in arquivos_na_pasta:
                    caminho_completo = os.path.join(destino_dir_convertida, arquivo)
                    if os.path.isfile(caminho_completo) and arquivo.lower().endswith(extensoes_validas):
                        contador_imagens += 1

                        img_name = caminho_completo
                        ada_img = cv2.imread(img_name)
                        ada_img = cv2.cvtColor(ada_img, cv2.COLOR_BGR2RGB)
                        ada_img = cv2.resize(ada_img, (180, 180), interpolation=cv2.INTER_AREA)

                        from keras.preprocessing import image
                        import numpy as np

                        ada_img = image.load_img(img_name, target_size=(180, 180))
                        x = image.img_to_array(ada_img)
                        x = np.expand_dims(x, axis=0)

                        pred = (model.predict(x) > 0.5).astype('int32')[0][0]

                        if pred == 1:
                            print(f"{arquivo}: Não Tem")
                            os.rename(f'{destino_dir}//{arquivo}', f'{pasta_nao_animal}//{arquivo}')
                        else:
                            contador_tem_animal += 1
                            print(f"{arquivo}: Tem")
                            os.rename(f'{destino_dir}//{arquivo}', f'{pasta_tem_animal}//{arquivo}')

                hoje = date.today()
                data_atual = hoje.strftime("%Y-%m-%d")

                try:
                    # Consulta IDs do funcionário e da câmera
                    id_funcionario = consultar_id_funcionario(user, cursor)
                    id_camera = consultar_id_camera(camera, cursor)

                    # Inserir na tabela de análise
                    insert_query = """INSERT INTO analise (id_funcionario, id_camera, data, total_analise, total_animal)
                                      VALUES (%s, %s, %s, %s, %s)"""

                    valores = (id_funcionario, id_camera, data_atual, contador_imagens, contador_tem_animal)

                    cursor.execute(insert_query, valores)
                    con.commit()
                    print("Dados inseridos com sucesso.")
                except ValueError as e:
                    print(f"Erro ao inserir dados: {e}")

            else:
                print("Nenhuma pasta foi selecionada.")

            cursor.close()
        finally:
            con.close()
    else:
        print("Não foi possível conectar ao banco de dados.")


#Função que registra usuário no banco
def registrar_usuario():
    def salvar_usuario():
        global contador_usuario
        nome_usuario = entrada_nome.get()
        setor_usuario = entrada_setor.get()
        unidade_usuario = entrada_unidade.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            query = "INSERT INTO funcionario (nome, setor, unidade) VALUES (%s, %s, %s)"
            valores = (nome_usuario, setor_usuario, unidade_usuario)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()

            resultado_label.config(text=f'Usuário cadastrado com sucesso!')
            resultado_label.place(x=35, y=330)

    janela_registro = tk.Tk()
    janela_registro.title("Registrar Usuário")
    janela_registro.geometry("575x410")
    janela_registro['bg'] = '#002a3a'
    janela_registro.resizable(0, 0)

    titulo = tk.Label(janela_registro, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
    titulo.place(x=140, y=70)

    frame_registro = tk.Frame(janela_registro, bg="#002a3a")
    frame_registro.place(x=90, y=150)

    label_nome = tk.Label(frame_registro, text="Nome do funcionário:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_nome.grid(row=0, column=0, padx=10, pady=5)
    entrada_nome = tk.Entry(frame_registro, font=("Arial", 12))
    entrada_nome.grid(row=0, column=1, padx=10, pady=5)

    label_setor = tk.Label(frame_registro, text="Setor do funcionário:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_setor.grid(row=1, column=0, padx=10, pady=5)
    entrada_setor = tk.Entry(frame_registro, font=("Arial", 12))
    entrada_setor.grid(row=1, column=1, padx=10, pady=5)

    label_unidade = tk.Label(frame_registro, text="Unidade do usuário:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_unidade.grid(row=2, column=0, padx=10, pady=5)
    entrada_unidade = tk.Entry(frame_registro, font=("Arial", 12))
    entrada_unidade.grid(row=2, column=1, padx=10, pady=5)

    botao_salvar = tk.Button(frame_registro, text="Salvar", command=salvar_usuario, font="Arial", width="7", bg="#808080", fg="White", border=3,
                             borderwidth=3)
    botao_salvar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    resultado_label = tk.Label(janela_registro, text="", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=35, y=330)

    janela_registro.mainloop()

#Função que consulta usuário no banco
def consultar_usuario():
    # Função que edita usuário no banco
    def editar_usuario():
        codigo_usuario = entrada_codigo.get()
        novo_nome = entrada_nome.get()
        novo_setor = entrada_setor.get()
        nova_unidade = entrada_unidade.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            query = "UPDATE funcionario SET nome = %s, setor = %s, unidade = %s WHERE id_funcionario = %s"
            valores = (novo_nome, novo_setor, nova_unidade, codigo_usuario)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()

            resultado_label.config(text='Usuário atualizado com sucesso!')
        else:
            resultado_label.config(text='Erro ao conectar ao banco de dados!')

    # Função que exibi usuário na tela
    def exibir_dados_usuario(usuario_id):
        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            query = "SELECT * FROM funcionario WHERE id_funcionario = %s"
            cursor.execute(query, (usuario_id,))
            usuario = cursor.fetchone()

            if usuario:
                entrada_nome.delete(0, tk.END)
                entrada_nome.insert(0, usuario['nome'])

                entrada_setor.delete(0, tk.END)
                entrada_setor.insert(0, usuario['setor'])

                entrada_unidade.delete(0, tk.END)
                entrada_unidade.insert(0, usuario['unidade'])
            else:
                print(f"Usuário com ID {usuario_id} não encontrado.")

            cursor.close()
            conexao.close()
        else:
            print("Erro ao conectar ao banco de dados.")

    # Função que seleciona usuário no banco
    def selecionar_usuario():
        codigo_usuario = entrada_codigo.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor(dictionary=True)  # Usar dictionary=True para retornar resultados como dicionários
            query = "SELECT * FROM funcionario WHERE id_funcionario = %s"
            cursor.execute(query, (codigo_usuario,))
            usuario = cursor.fetchone()
            cursor.close()
            conexao.close()

            if usuario:
                exibir_dados_usuario(usuario['id_funcionario'])
                botao_editar.config(state=tk.NORMAL)
                resultado_label.config(text='Usuário encontrado!')
            else:
                resultado_label.config(text='Usuário não encontrado!')
                botao_editar.config(state=tk.DISABLED)
        else:
            resultado_label.config(text='Erro ao conectar ao banco de dados!')
            botao_editar.config(state=tk.DISABLED)

#JANELA EDITAR FUNCIONARIO
    janela_consulta = tk.Toplevel(janela)
    janela_consulta.title("Consultar Usuário")
    janela_consulta.geometry("575x410")
    janela_consulta['bg'] = '#002a3a'
    janela_consulta.resizable(0, 0)

    titulo = tk.Label(janela_consulta, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
    titulo.place(x=145, y=60)

    frame_consulta = tk.Frame(janela_consulta, bg="#002a3a")
    frame_consulta.place(x=85, y=130)

    label_codigo = tk.Label(frame_consulta, text="Código do usuário:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_codigo.grid(row=0, column=0, padx=10, pady=5)
    entrada_codigo = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_codigo.grid(row=0, column=1, padx=10, pady=5)

    botao_buscar = tk.Button(frame_consulta, text="Buscar", command=selecionar_usuario, font="Arial", width="7",
                             bg="#808080", fg="White", border=3,
                             borderwidth=3)
    botao_buscar.grid(row=4, column=1, padx=10, pady=5)

    label_nome = tk.Label(frame_consulta, text="Nome do funcionário:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_nome.grid(row=1, column=0, padx=10, pady=5)
    entrada_nome = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_nome.grid(row=1, column=1, padx=10, pady=5)

    label_setor = tk.Label(frame_consulta, text="Setor do funcionário:", font=("Arial 12 bold"), bg="#002a3a",
                           fg="white")
    label_setor.grid(row=2, column=0, padx=10, pady=5)
    entrada_setor = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_setor.grid(row=2, column=1, padx=10, pady=5)

    label_unidade = tk.Label(frame_consulta, text="Unidade do usuário:", font=("Arial 12 bold"), bg="#002a3a",
                             fg="white")
    label_unidade.grid(row=3, column=0, padx=10, pady=5)
    entrada_unidade = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_unidade.grid(row=3, column=1, padx=10, pady=5)

    botao_editar = tk.Button(frame_consulta, text="Editar", command=editar_usuario, font="Arial", width="7",
                             bg="#808080", fg="White", border=3,
                             borderwidth=3, state=tk.DISABLED)
    botao_editar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    resultado_label = tk.Label(janela_consulta, text="", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=190, y=340)

#Função que lista todos os usuários cadastrados no banco
def listar_usuario_cadastrado():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Lista de Usuários Cadastrados")
    nova_janela.geometry("550x400")
    nova_janela['bg'] = '#002a3a'

    resultado_label = tk.Label(nova_janela, font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=175, y=100)

    trv = ttk.Treeview(nova_janela, selectmode='browse')
    trv.place(x=115, y=70)

    trv["columns"] = ("1", "2", "3", "4")
    trv['show'] = 'headings'

    trv.column("1", width=85, anchor='c')
    trv.column("2", width=85, anchor='c')
    trv.column("3", width=85, anchor='c')
    trv.column("4", width=85, anchor='c')

    trv.heading("1", text="Código")
    trv.heading("2", text="Nome")
    trv.heading("3", text="Setor")
    trv.heading("4", text="Unidade")



    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM funcionario")
        registros = cursor.fetchall()
        cursor.close()
        conexao.close()

        if not registros:
            resultado_label.config(text='Nenhum usuário cadastrado.')
            resultado_label.place(x=175, y=40)
        else:
            for registro in registros:
                trv.insert("", 'end', values=(registro[0], registro[1], registro[2], registro[3]))

    botao_fechar = tk.Button(nova_janela, text="Fechar", command=nova_janela.destroy, font="Arial", width="7", bg="#808080", fg="White", border=3,
                        borderwidth=3)
    botao_fechar.place(x=245, y=330)


#Função que registra camera no banco
def registrar_camera():
    def salvar_camera():
        global contador_CAM
        nome_camera = entrada_nome_camera.get()
        setor_camera = entrada_setor.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            query = "INSERT INTO camera (nome_camera, setor_camera) VALUES (%s, %s)"
            valores = (nome_camera, setor_camera)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()

            resultado_label.config(text=f'Câmera cadastrada com sucesso!')
            resultado_label.place(x=35, y=330)

    janela_registro = tk.Tk()
    janela_registro.title("Registrar Câmera")
    janela_registro.geometry("575x410")
    janela_registro.resizable(0, 0)
    janela_registro['bg'] = '#002a3a'

    titulo = tk.Label(janela_registro, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
    titulo.place(x=140, y=70)

    frame_registro = tk.Frame(janela_registro, bg="#002a3a")
    frame_registro.place(x=100, y=140)

    label_nome = tk.Label(frame_registro, text="Nome da câmera: ", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_nome.grid(row=0, column=0, padx=10, pady=5)
    entrada_nome_camera = tk.Entry(frame_registro, font=("Arial", 12))
    entrada_nome_camera.grid(row=0, column=1, padx=10, pady=5)

    label_setor = tk.Label(frame_registro, text="Setor da câmera: ", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_setor.grid(row=1, column=0, padx=10, pady=5)
    entrada_setor = tk.Entry(frame_registro, font=("Arial", 12))
    entrada_setor.grid(row=1, column=1, padx=10, pady=5)

    botao_salvar = tk.Button(frame_registro, text="Salvar", command=salvar_camera, font="Arial", width="7", bg="#808080", fg="White", border=3,
                             borderwidth=3)
    botao_salvar.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    resultado_label = tk.Label(janela_registro, text="", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=35, y=330)

    janela_registro.mainloop()

#Função que consulta camera no banco
def consultar_camera():
    # Função que edita camera no banco
    def editar_camera():
        novo_setor = entrada_setor.get()
        nova_camera = entrada_camera.get()
        codigo_CAM = entrada_codigo.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor()
            query = "UPDATE camera SET nome_camera = %s, setor_camera = %s WHERE id_camera = %s"
            valores = (nova_camera, novo_setor, codigo_CAM)
            cursor.execute(query, valores)
            conexao.commit()
            cursor.close()
            conexao.close()

            resultado_label.config(text='Câmera atualizada com sucesso!')
        else:
            resultado_label.config(text='Erro ao conectar ao banco de dados!')

    # Função para exibir  câmera selecionada
    def exibir_dados_camera(camera):
        entrada_setor.delete(0, tk.END)
        entrada_setor.insert(0, camera['setor_camera'])

        entrada_camera.delete(0, tk.END)
        entrada_camera.insert(0, camera['nome_camera'])

    # Função para selecionar câmera no banco
    def selecionar_camera():
        codigo_CAM = entrada_codigo.get()

        conexao = conectar_db()
        if conexao:
            cursor = conexao.cursor(dictionary=True)
            query = "SELECT * FROM camera WHERE id_camera = %s"
            cursor.execute(query, (codigo_CAM,))
            camera = cursor.fetchone()
            cursor.close()
            conexao.close()

            if camera:
                exibir_dados_camera(camera)
                botao_editar.config(state=tk.NORMAL)
                resultado_label.config(text='Câmera encontrada!')
            else:
                resultado_label.config(text='Câmera não encontrada!')
                botao_editar.config(state=tk.DISABLED)
        else:
            resultado_label.config(text='Erro ao conectar ao banco de dados!')
            botao_editar.config(state=tk.DISABLED)
#JANELA EDITAR CAMERA
    janela_consulta = tk.Toplevel(janela)
    janela_consulta.title("Consultar Câmera")
    janela_consulta.geometry("575x410")
    janela_consulta.resizable(0, 0)
    janela_consulta['bg'] = '#002a3a'

    titulo = tk.Label(janela_consulta, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
    titulo.place(x=145, y=60)

    frame_consulta = tk.Frame(janela_consulta, bg="#002a3a")
    frame_consulta.place(x=95,y=140)

    label_codigo = tk.Label(frame_consulta, text="Código da câmera:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_codigo.grid(row=0, column=0, padx=10, pady=5)
    entrada_codigo = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_codigo.grid(row=0, column=1, padx=10, pady=5)

    botao_buscar = tk.Button(frame_consulta, text="Buscar", command=selecionar_camera, font="Arial", width="7", bg="#808080", fg="White", border=3,
                        borderwidth=3)
    botao_buscar.grid(row=4, column=1, padx=10, pady=5)

    label_setor = tk.Label(frame_consulta, text="Setor:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_setor.grid(row=2, column=0, padx=10, pady=5)
    entrada_setor = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_setor.grid(row=2, column=1, padx=10, pady=5)

    label_camera = tk.Label(frame_consulta, text="Nome da câmera:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    label_camera.grid(row=3, column=0, padx=10, pady=5)
    entrada_camera = tk.Entry(frame_consulta, font=("Arial", 12))
    entrada_camera.grid(row=3, column=1, padx=10, pady=5)

    botao_editar = tk.Button(frame_consulta, text="Editar", command=editar_camera, font="Arial", width="7", bg="#808080", fg="White", border=3,
                        borderwidth=3, state=tk.DISABLED)
    botao_editar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    resultado_label = tk.Label(janela_consulta, text="", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=190, y=340)

#função que lista todas as cameras cadastradas no banco
def listar_camera_cadastrada():
    nova_janela = tk.Toplevel(janela)
    nova_janela.title("Lista de Câmeras Cadastradas")
    nova_janela.geometry("550x400")
    nova_janela['bg'] = '#002a3a'

    resultado_label = tk.Label(nova_janela, font=("Arial 12 bold"), bg="#002a3a", fg="white")
    resultado_label.place(x=175, y=100)

    trv = ttk.Treeview(nova_janela, selectmode='browse')
    trv.place(x=155, y=70)

    trv["columns"] = ("1", "2", "3")
    trv['show'] = 'headings'

    trv.column("1", width=85, anchor='c')
    trv.column("2", width=85, anchor='c')
    trv.column("3", width=85, anchor='c')

    trv.heading("1", text="Código")
    trv.heading("2", text="Setor")
    trv.heading("3", text="Câmera")



    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM camera")
        registros = cursor.fetchall()
        cursor.close()
        conexao.close()

        if not registros:
            resultado_label.config(text='Nenhuma câmera cadastrada.')
            resultado_label.place(x=175, y=40)
        else:
            for registro in registros:
                trv.insert("", 'end', values=(registro[0], registro[1], registro[2]))

    botao_fechar = tk.Button(nova_janela, text="Fechar", command=nova_janela.destroy, font="Arial", width="7", bg="#808080", fg="White", border=3,
                        borderwidth=3)
    botao_fechar.place(x=245, y=330)

#Exibe o caminho selecinado na tela
def mostrar_caminho():
    caminho = selecionar_pasta()  # Chama a função na outra pasta

    if caminho:  # se for selecionada alguma pasta
        entrada.delete(0, tk.END)  # Limpa a entry
        entrada.insert(0, caminho)  # Coloca o arquivo selecionado na Entry
    else:  # Se nao for selecionada nenhuma pasta
        entrada.delete(0, tk.END)  # Limpa a entry
        entrada.insert(0, 'Nenhuma pasta selecionada')  # coloca o texto na entry

#Executa a IA
def executar_IA():
    caminho = entrada.get()
    camera = select_cam.get()
    user = select_user.get()


    if caminho:
        execucao(caminho, camera, user)

        j = tk.Tk()
        j.geometry("300x200")
        j['bg'] = '#002a3a'
        j.resizable(0, 0)

        jtexto = tk.Label(j, text="A operação foi realizada com sucesso.", font=("Lato 10 bold"), bg='#002a3a', fg="white")
        jtexto.place(x=30, y=60)

        j.mainloop()
    else:
        messagebox.showinfo("ERRO", "Nenhuma pasta selecionada pelo usuário")


def abrir_execucao_ia():
    global entrada
    global select_user
    global select_cam

    def conectar_db():
        try:
            con = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="projeto_guapiacu"
            )
            return con
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados: {err}")
            return None

    def atualizar_combobox_usuarios():
        conexao = conectar_db()

        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM funcionario")
            usuarios = cursor.fetchall()
            cursor.close()
            conexao.close()

            select_user['values'] = [usuario[0] for usuario in usuarios]
            select_user.set("*Selecione o Usuário")
        else:
            print("Erro ao conectar ao banco de dados para atualizar usuários")

    # Função para atualizar ComboBox de câmeras
    def atualizar_combobox_cameras():
        conexao = conectar_db()

        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome_camera FROM camera")
            cameras = cursor.fetchall()
            cursor.close()
            conexao.close()

            select_cam['values'] = [camera[0] for camera in cameras]
            select_cam.set("*Selecione a Câmera")
        else:
            print("Erro ao conectar ao banco de dados para atualizar câmeras")

    titulo = tk.Label(janela, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
    titulo.place(x=140, y=60)

    tirar_label = tk.Label(janela, text="                           ", font=("Arial 30 bold"), bg="#002a3a",
                               fg="white")
    tirar_label.place(x=135, y=130)

    itexto = tk.Label(janela, text="*Selecione uma pasta:", font=("Arial 12 bold"), bg="#002a3a", fg="white")
    itexto.place(x=90, y=175)

    entrada = tk.Entry(janela, width="33", border="2", borderwidth="5", font="Arial")
    entrada.place(x=90, y=200)

    selecao = tk.Button(janela, text="Selecionar", font="Arial", width="9", bg="#808080", fg="White", border=3,
                        borderwidth=3, command=mostrar_caminho)
    selecao.place(x=420, y=199)

    iniciar = tk.Button(janela, text="Inicializar", font="Arial", width="9", command=executar_IA, bg="#808080",
                        fg="White", border=3, borderwidth=3)
    iniciar.place(x=420, y=319)

    usuarios = ["*Selecione o Usuário"]
    select_user = ttk.Combobox(janela, values=usuarios)
    select_user.set(usuarios[0])
    select_user.place(x=140, y=130)


    cameras = ["*Selecione a Câmera"]
    select_cam = ttk.Combobox(janela, values=cameras)
    select_cam.set(cameras[0])
    select_cam.place(x=290, y=130)


    # Atualiza as ComboBoxes de usuários e câmeras ao abrir a janela
    atualizar_combobox_usuarios()
    atualizar_combobox_cameras()

def abrir_analise_ia():
    analise_ia = tk.Toplevel(janela)  # Cria uma nova janela secundária
    analise_ia.title("Lista de cameras Cadastradas")
    analise_ia.geometry("550x400")
    analise_ia['bg'] = '#002a3a'

    resultado_label = tk.Label(analise_ia, font=("Arial 12 bold"), bg="#002a3a", fg="white")


    trv = ttk.Treeview(analise_ia, selectmode='browse')
    trv.place(x=50, y=70)

    trv["columns"] = ("1", "2", "3", "4", "5", "6")
    trv['show'] = 'headings'

    trv.column("1", width=75, anchor='c')
    trv.column("2", width=75, anchor='c')
    trv.column("3", width=75, anchor='c')
    trv.column("4", width=75, anchor='c')
    trv.column("5", width=75, anchor='c')
    trv.column("6", width=75, anchor='c')

    trv.heading("1", text="ID_Análise")
    trv.heading("2", text="ID_Funcionário")
    trv.heading("3", text="ID_Câmera")
    trv.heading("4", text="Data")
    trv.heading("5", text="total_analise")
    trv.heading("6", text="total_animal")

    conexao = conectar_db()
    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM analise")
        registros = cursor.fetchall()
        cursor.close()
        conexao.close()

        if not registros:
            resultado_label.config(text='Nenhuma análise cadastrado.')
            resultado_label.place(x=175, y=40)
        else:
            for registro in registros:
                trv.insert("", 'end', values=(registro[0], registro[1], registro[2], registro[3],registro[4],registro[5]))

    botao_fechar = tk.Button(analise_ia, text="Fechar", command=analise_ia.destroy, font="Arial", width="7",
                             bg="#808080", fg="White", border=3,
                             borderwidth=3)
    botao_fechar.place(x=245, y=330)







# Cria a janela principal
janela = tk.Tk()
janela.title("Tela Principal")
janela.geometry("575x410")
janela['bg'] = '#002a3a'
janela.resizable(0, 0)


# Cria o Título e Texto
titulo = tk.Label(janela, text="Projeto Guapiaçu", font=("Lato 26 bold"), bg="#002a3a", fg="white")
titulo.place(x=145, y=60)

label_instrucao = tk.Label(janela, text="*Selecione uma opção no menu acima.", font=("Arial 13 bold"), bg="#002a3a", fg="white")
label_instrucao.place(x=135, y=130)

# Cria a barra de menu
menu_principal = tk.Menu(janela)
janela.config(menu=menu_principal)

# Cria o submenu "Usuário"
submenu_usuario = tk.Menu(menu_principal, tearoff=0)
submenu_usuario.add_command(label="Cadastrar", command=registrar_usuario)
submenu_usuario.add_command(label="Consultar", command=listar_usuario_cadastrado)
submenu_usuario.add_command(label="Editar", command=consultar_usuario)
menu_principal.add_cascade(label="Usuário", menu=submenu_usuario)

# Cria o submenu "Unidade"
submenu_unidade = tk.Menu(menu_principal, tearoff=0)
submenu_unidade.add_command(label="Cadastrar", command=registrar_camera)
submenu_unidade.add_command(label="Consultar", command=listar_camera_cadastrada)
submenu_unidade.add_command(label="Editar", command=consultar_camera)
menu_principal.add_cascade(label="Camera", menu=submenu_unidade)

# Cria o submenu "Inventário"
submenu_inventario = tk.Menu(menu_principal, tearoff=0)
submenu_inventario.add_command(label="Executar IA", command=abrir_execucao_ia)
submenu_inventario.add_command(label="Ver Análises", command=abrir_analise_ia)
menu_principal.add_cascade(label="IA", menu=submenu_inventario)






# Executa a janela principal
janela.mainloop()
