import mysql.connector

# Conectar ao banco de dados
con = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='',
    database='projeto_guapiacu'
)

cursor = con.cursor()

print(con)

#cursor.execute('create database projeto_guapiacu')

# Criação da tabela 'funcionario'
cursor.execute('''CREATE TABLE IF NOT EXISTS funcionario(
                id_funcionario INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(30) NOT NULL,
                setor VARCHAR(60) NOT NULL,
                unidade VARCHAR(60) NOT NULL)''')
con.commit()

# Criação da tabela 'camera'
cursor.execute('''CREATE TABLE IF NOT EXISTS camera(
                 id_camera INT PRIMARY KEY AUTO_INCREMENT,
                 nome_camera VARCHAR(30) NOT NULL,
                 setor_camera VARCHAR(60) NOT NULL)''')
con.commit()

# Criação da tabela 'analise'
cursor.execute('''CREATE TABLE IF NOT EXISTS analise(
                 id_analise INT PRIMARY KEY AUTO_INCREMENT,
                 id_funcionario INT NOT NULL,
                 id_camera INT NOT NULL,
                 data DATE NOT NULL,
                 total_analise INT NOT NULL,
                 total_animal INT NOT NULL,
                 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario),
                 FOREIGN KEY (id_camera) REFERENCES camera(id_camera))''')
con.commit()

# Fechar cursor e conexão
cursor.close()
con.close()
