import flet as ft
import os
from models import Usuario, SessionLocal, Treino, QuestionarioDor
from funcoes import df_gifs, criar_card

def main(page: ft.Page): # Alterado para async def
    page.vertical_alignment = "stretch"
    page.horizontal_alignment = "stretch"
    
    if 'loggedIn' not in page.session.get_keys():
        page.session.set('loggedIn', False)
    if 'current_username' not in page.session.get_keys():
        page.session.set('current_username', None)
    if 'usuario_id' not in page.session.get_keys():
        page.session.set('usuario_id', None)
        
    email_field = ft.TextField(label='Email', width=300)
    senha_field = ft.TextField(label='Senha', password=True, can_reveal_password=True, width=300)
    
    def login_click(e):
        with SessionLocal() as db:
            user = db.query(Usuario).filter_by(email=email_field.value, senha=senha_field.value).first()
            if user:
                page.session.set('loggedIn', True)
                ft.Text('Bem vindo!', color='green')
                page.session.set('usuario_id', user.id)
                page.go('/')
            else:
                ft.Text('Não encontrado!', color='red')
            page.update()
                
    def login_page():
        login_button = ft.ElevatedButton('Login', on_click=login_click)
        return ft.View(
            "/login", # Rota desta View
            controls=[
                # AppBar para a página de login (opcional, mas bom para consistência)
                ft.AppBar(title=ft.Text("Login", weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.BLUE_GREY_700, center_title=True,),
                ft.Column(
                    [
                        ft.Text("Bem-vindo! Faça seu login", size=24, weight=ft.FontWeight.BOLD),
                        email_field,
                        senha_field,
                        login_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                )
            ],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    
    def tem_Exercicios(treino):
        for i in treino:
            if i.exercicios:
                return True
            else:
                return False 
            
    def home():
        usuario_id = page.session.get('usuario_id')
        
        col_lista_treinos = ft.Column()
        # col_lista_treinos.height = page.height * 0.05
        texto = ft.Text()
        row2 = ft.Row()
        row2.height = page.height * 0.5
        row2.scroll = 'auto'
        
        with SessionLocal() as db:
            # Carrega os treinos disponíveis no dropdown
            usuario = db.query(Usuario).filter_by(id=usuario_id).first()
            nomes_treinos = [x.nome for x in db.query(Treino).filter_by(usuario_id=usuario_id).all()]
        
        # Função chamada ao selecionar um item no dropdown
        def dropdown_chama(e):
            dropdown_selected = str(e.control.value)
            with SessionLocal() as db:
                treino_selected = db.query(Treino).filter_by(usuario_id=usuario_id, nome=dropdown_selected).all()
            
                texto.value = dropdown_selected
            
                if tem_Exercicios(treino=treino_selected):
                    # Achatar a lista de exercícios e criar Texts
                    exercicios_series_repeticoes = [{'Nome':x.exercicios.nome, 'Séries': x.exercicios.series, 'Repetições': x.exercicios.repeticoes} for x in treino_selected]
                    for item in exercicios_series_repeticoes:
                        if not df_gifs[df_gifs['Arquivo'].str.contains(item['Nome'], case=False, na=False)].empty:
                            v = df_gifs[df_gifs['Arquivo'].str.contains(item['Nome'], case=False, na=False)]['Arquivo'].values
                            item['Gif'] = v[0]
                else:
                    exercicios_series_repeticoes = []
                col_lista_treinos.controls = [ft.Text(f"- {x['Nome']}", size=16, weight='bold') for x in exercicios_series_repeticoes] or [ft.Text("Ainda não existe exrecícios para este treino!", color='red')]
                row2.controls = [criar_card(nome=x['Nome'], series=x['Séries'], repeticoes=x['Repetições'], imagem_url=f"imagens/{x['Gif']}" if 'Gif' in x else None, page=page) 
                                    for x in exercicios_series_repeticoes]
            page.update()

        # Dropdown populado com nomes dos treinos
        dropdown1 = ft.Dropdown(
            label='Selecione um treino',
            options=[ft.dropdown.Option(x) for x in sorted(set(nomes_treinos))],
            on_change=dropdown_chama,
            width=300
        )
        
        return ft.View(
            "/",
            controls=[
                ft.AppBar(
                    title=ft.Text("Página Inicial", weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.BLUE_GREY_700, 
                    center_title=True,
                    actions=[
                        ft.Row(
                            spacing=15,
                            controls=[
                                ft.ElevatedButton('Questionario', on_click= lambda _: page.go('/questionario')),
                                ft.ElevatedButton("Sair", on_click=lambda _: page.go('/login')),
                            ],
                        )
                    ]
                ),
                ft.Column(
                    scroll='auto',
                    controls=[
                                ft.Row(
                                    spacing=page.width * 0.2,
                                    controls=[
                                        ft.Text(f"Olá, {usuario.nome}!", size=24, weight="bold"),
                                        
                                    ],
                                ),
                                ft.Divider(),
                                ft.Row(
                                    height=page.height * 0.4,
                                    controls=[
                                        ft.Card(
                                            content=ft.Column(
                                                controls=[
                                                    dropdown1
                                                ]
                                            )
                                            ),
                                        ft.Card(
                                            content=ft.Container(
                                                content=ft.Column(
                                                            scroll='auto',
                                                            alignment=ft.MainAxisAlignment.CENTER,
                                                            controls=[
                                                                ft.Text('Exercícios', size=20, weight='bold'),
                                                                col_lista_treinos,
                                                            ]
                                                        )
                                            ),
                                        ),
                                    ],
                                    scroll='auto'
                                ),
                                ft.Divider(),
                                ft.Row(
                                    scroll='auto',
                                    controls=[
                                        ft.Card(
                                            content=ft.Container(
                                                content=ft.Row([
                                                    ft.Row([row2],expand=1, scroll='auto'),
                                                ],
                                                scroll='auto'
                                                )
                                            ),
                                        ),
                                    ]
                                )
                            ],
                        )
            ],
            scroll='auto'
    )
    
    # Criar referências para os Dropdowns
    pre_pos_ref = ft.Ref[ft.Dropdown]()
    local_ref = ft.Ref[ft.Dropdown]()
    intensidade_ref = ft.Ref[ft.Dropdown]()

    resultado = ft.Text()

    # Função para criar os Dropdowns dinamicamente
    def criar_dropdowns():
        return [
            ft.Dropdown(
                ref=pre_pos_ref,
                label="Pré ou Pós treino?",
                options=[ft.dropdown.Option("Pré"), ft.dropdown.Option("Pós")],
                width=300
            ),
            ft.Dropdown(
                ref=local_ref,
                label="Qual parte do corpo?",
                options=[ft.dropdown.Option(str(i)) for i in range(0, 54)],
                width=300
            ),
            ft.Dropdown(
                ref=intensidade_ref,
                label="Qual intensidade da dor?",
                options=[ft.dropdown.Option(str(i)) for i in range(0, 11)],
                width=300
            )
        ]

    # Container que irá segurar os Dropdowns
    form_column = ft.Column(controls=criar_dropdowns())

    def enviar(e):
        usuario_id = page.session.get('usuario_id')
        pre_pos_treino = pre_pos_ref.current.value
        local = local_ref.current.value
        intensidade = intensidade_ref.current.value

        if not pre_pos_treino or not local or not intensidade:
            resultado.value = "Preencha os campos!"
            resultado.color = "red"
        else:
            with SessionLocal() as db:
                resposta = QuestionarioDor(
                usuario_id = usuario_id,
                pre_pos_treino = pre_pos_treino,
                local = local,
                intensidade = intensidade
                )
                db.add(resposta)
                db.commit()
            
            resultado.value = "Formulário enviado!"
            resultado.color = "green"

            # 🔁 Recriar os dropdowns para limpá-los visualmente
            form_column.controls = criar_dropdowns()
            form_column.update()

        resultado.update()
    enviar_button = ft.ElevatedButton("Enviar", on_click=enviar)
    
    def QuestionarioView():
        
        return ft.View(
                    route="/questionario",
                    spacing=20,
                    scroll='auto',
                    padding=30,
                    controls=[
                        ft.AppBar(
                        title=ft.Text("Questionário", weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.BLUE_GREY_700, 
                        center_title=True,
                        actions=[
                            ft.Row(
                                spacing=15,
                                alignment='end',
                                controls=[
                                    ft.ElevatedButton('Página Inicial', on_click= lambda _: page.go('/')),
                                    ft.ElevatedButton("Sair", on_click=lambda _: page.go('/login')),
                                ]
                            )
                            
                        ]
                        ),
                        ft.Row(
                            expand=1,
                            controls=[
                                ft.Column(
                                        expand=1,
                                        controls=[
                                            ft.Image(src='imagens/imagem_corpo_numeros.jpeg', fit=ft.ImageFit.CONTAIN)
                                        ]
                                    ),
                                ft.Column(
                                    expand=1,
                                    controls=[
                                    ft.Text("Formulário de Dor", size=24, weight="bold"),
                                    form_column,
                                    enviar_button,
                                    resultado
                                    ]
                                )
                            ]
                            
                        )
                    ]
                )
                
    def route_change(route):
        page.views.clear()
        
        # Se não estiver logado
        if not page.session.get('loggedIn') and page.route != '/login':
            page.go('/login')
            return
        
        if page.route == '/login':
            page.views.append(login_page())
        elif page.route == '/':
            page.views.append(home())
        elif page.route == '/questionario':
            page.views.append(QuestionarioView())
        page.update()
        
    page.on_route_change = route_change
    page.go(page.route)
    
# Inicia a aplicação Flet.
# ft.app(target=main) para rodar como app desktop
# ft.app(target=main, view=ft.WEB_BROWSER) para rodar no navegador
# if __name__ == "__main__":
#     ft.app(target=main, view=ft.WEB_BROWSER)
# No final do main.py
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8550))
#     host = os.environ.get("HOST", "0.0.0.0")

#     # Capture a instância da aplicação Flet
#     # Nomeie a variável globalmente para Uvicorn encontrar
#     global ft_app_instance
#     ft_app_instance = ft.app(target=main, view=ft.WEB_BROWSER, port=port, host=host)

# Render usa variáveis de ambiente de porta, o Flet cuida disso automaticamente em modo web.
ft.app(target=main, view=ft.WEB_BROWSER)