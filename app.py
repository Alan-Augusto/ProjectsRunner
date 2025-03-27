import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget, QDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QIcon

class ProjectManagerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Projects Runner")
        self.setFixedSize(400, 500)
        self.projects = []
        self.is_dark_theme = True

        # Definir o ícone da janela
        self.setWindowIcon(QIcon('./assets/terminal.png'))  # Substitua pelo caminho do seu ícone

        # Estilo inicial
        self.set_style()

        # Carregar projetos salvos
        self.load_projects()

        # Interface
        self.create_widgets()

    def set_style(self):
        # Tema claro e escuro
        palette = self.palette()

        if self.is_dark_theme:
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.Button, QColor(50, 50, 50))
            palette.setColor(QPalette.Highlight, QColor(100, 100, 100))
            self.setStyleSheet("""
                QWidget {
                    font-family: Arial, sans-serif;
                    background-color: #1e1e1e;
                    color: white;
                }
                QLineEdit, QPushButton, QListWidget {
                    border-radius: 10px;
                    padding: 8px;
                    background-color: #2b2b2b;
                    color: white;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                }
                QPushButton {
                    background-color: #A0A0A0;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #707070;
                }
                QPushButton:pressed {
                    background-color: #505050;
                }
                QListWidget {
                    background-color: #2b2b2b;
                    border: 1px solid #444;
                    color: white;
                }
            """)
        else:
            palette.setColor(QPalette.Window, QColor(245, 245, 245))
            palette.setColor(QPalette.Button, QColor(235, 235, 235))
            palette.setColor(QPalette.Highlight, QColor(100, 100, 100))
            self.setStyleSheet("""
                QWidget {
                    font-family: Arial, sans-serif;
                }
                QLineEdit, QPushButton, QListWidget {
                    border-radius: 10px;
                    padding: 8px;
                    background-color: #f0f0f0;
                }
                QLineEdit {
                    background-color: #ffffff;
                }
                QPushButton {
                    background-color: #A0A0A0;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #707070;
                }
                QPushButton:pressed {
                    background-color: #505050;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                }
            """)

        self.setPalette(palette)

    def create_widgets(self):
        # Layout principal
        main_layout = QVBoxLayout()

        # Layout para o título e o botão de tema (topo da tela)
        top_layout = QHBoxLayout()

        # Espaço vazio à esquerda do título para centralização
        left_spacer = QLabel("", self)
        left_spacer.setFixedWidth(40)  # Ajuste o tamanho conforme necessário
        top_layout.addWidget(left_spacer, alignment=Qt.AlignLeft)

        # Título do aplicativo centralizado com fonte maior
        title_label = QLabel("Projects Runner", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Botão de alternância de tema (sol/lua) à direita
        self.theme_button = QPushButton(self)
        self.theme_button.setIcon(QIcon("./assets/sun.png" if self.is_dark_theme else "./assets/moon.png"))
        self.theme_button.clicked.connect(self.toggle_theme)
        top_layout.addWidget(self.theme_button, alignment=Qt.AlignRight)

        # Adiciona o layout do topo no layout principal
        main_layout.addLayout(top_layout)

        # Layout para os campos de entrada
        form_layout = QVBoxLayout()

        # Nome do projeto
        self.project_name = QLineEdit(self)
        self.project_name.setPlaceholderText("Nome do Projeto")
        form_layout.addWidget(self.project_name)

        # Caminho do projeto
        self.project_path = QLineEdit(self)
        self.project_path.setPlaceholderText("Caminho do Projeto")
        form_layout.addWidget(self.project_path)

        # Botão de selecionar pasta
        self.select_button = QPushButton("Selecionar Pasta", self)
        self.select_button.clicked.connect(self.select_folder)
        form_layout.addWidget(self.select_button)

        # Comando para execução
        self.project_command = QLineEdit(self)
        self.project_command.setPlaceholderText("Comando para Execução")
        form_layout.addWidget(self.project_command)

        main_layout.addLayout(form_layout)

        # Botões de ação
        action_layout = QHBoxLayout()

        self.add_button = QPushButton("Adicionar Projeto", self)
        self.add_button.clicked.connect(self.add_project)
        action_layout.addWidget(self.add_button)

        self.run_button = QPushButton("Rodar Projetos", self)
        self.run_button.clicked.connect(self.run_projects)
        action_layout.addWidget(self.run_button)

        self.delete_button = QPushButton("Apagar Projeto", self)
        self.delete_button.clicked.connect(self.delete_project)
        action_layout.addWidget(self.delete_button)

        main_layout.addLayout(action_layout)

        # Lista de projetos
        self.projects_listbox = QListWidget(self)
        main_layout.addWidget(self.projects_listbox)

        # Preenche a lista de projetos com os projetos carregados
        self.update_project_list()

        self.setLayout(main_layout)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.set_style()
        self.theme_button.setIcon(QIcon("./assets/sun.png" if self.is_dark_theme else "./assets/moon.png"))

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if folder:
            self.project_path.setText(folder)

    def add_project(self):
        name = self.project_name.text()
        path = self.project_path.text()
        command = self.project_command.text()

        if not name or not path or not command:
            self.show_error("Erro", "Preencha todos os campos!")
            return

        project = {"name": name, "path": path, "command": command}
        self.projects.append(project)
        self.projects_listbox.addItem(name)

        # Limpar campos após adicionar
        self.project_name.clear()
        self.project_path.clear()
        self.project_command.clear()

        # Salvar os projetos em um arquivo JSON
        self.save_projects()

    def delete_project(self):
        selected_items = self.projects_listbox.selectedItems()

        if not selected_items:
            self.show_error("Erro", "Selecione um projeto para apagar.")
            return

        # Remove o projeto da lista
        selected_name = selected_items[0].text()
        self.projects = [proj for proj in self.projects if proj["name"] != selected_name]

        # Atualiza a listbox
        self.update_project_list()

        # Salvar os projetos após exclusão
        self.save_projects()

    def update_project_list(self):
        # Limpa a listbox antes de atualizar
        self.projects_listbox.clear()

        # Adiciona os projetos à listbox
        for project in self.projects:
            self.projects_listbox.addItem(project["name"])

    def run_projects(self):
        for project in self.projects:
            name = project["name"]
            path = project["path"]
            command = project["command"]

            try:
                # Verifica se o caminho existe
                if not os.path.exists(path):
                    self.show_error("Erro", f"Caminho inválido para o projeto {name}")
                    continue

                # Executar comando no terminal (Windows)
                if os.name == 'nt':  # Windows
                    subprocess.Popen(f'start cmd /k "cd {path} && {command}"', shell=True)
                else:  # Linux ou MacOS
                    subprocess.Popen(f'gnome-terminal --working-directory={path} -- bash -c "{command}; exec bash"')
            except Exception as e:
                self.show_error("Erro", f"Erro ao tentar rodar o projeto {name}: {e}")

    def save_projects(self):
        try:
            with open("./data/projects.json", "w") as f:
                json.dump(self.projects, f)
        except Exception as e:
            self.show_error("Erro", f"Erro ao salvar os projetos: {e}")

    def load_projects(self):
        if os.path.exists("./data/projects.json"):
            try:
                with open("./data/projects.json", "r") as f:
                    self.projects = json.load(f)
            except Exception as e:
                self.show_error("Erro", f"Erro ao carregar os projetos: {e}")

    def show_error(self, title, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectManagerApp()
    window.show()
    sys.exit(app.exec_())
