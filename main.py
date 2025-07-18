import flet as ft
import os
from models import Usuario, SessionLocal, Treino, QuestionarioDor, ExercicioPrescrito
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
    
    login_alerta = ft.AlertDialog(
        title=ft.Text("Login Negado!"),
        content=ft.Text("Email ou senha incorreto!"),
        alignment=ft.alignment.center,
        # on_dismiss=lambda e: print("Dialog dismissed!"),
        title_padding=ft.padding.all(25),
    )
    
    def login_click(e):
        with SessionLocal() as db:
            user = db.query(Usuario).filter_by(email=email_field.value, senha=senha_field.value).first()
            if user:
                page.session.set('loggedIn', True)
                ft.Text('Bem vindo!', color='green')
                page.session.set('usuario_id', user.id)
                page.go('/')
            else:
                page.open(login_alerta)
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
        if treino.exercicios_prescritos:
            return True
        else:
            return False 
            
    def home():
        usuario_id = page.session.get('usuario_id')
        
        col_lista_treinos = ft.Column()
        # col_lista_treinos.scroll = ft.ScrollMode.AUTO
        texto = ft.Text()
        row2 = ft.Row()
        row2.height = page.height * 0.5
        row2.scroll = 'auto'
        
        with SessionLocal() as db:
            # Carrega os treinos disponíveis no dropdown
            usuario = db.query(Usuario).filter_by(id=usuario_id).first()
            nomes_treinos = [x.titulo for x in db.query(Treino).filter_by(usuario_id=usuario_id).all()]
        
        # Função chamada ao selecionar um item no dropdown
        def dropdown_chama(e):
            dropdown_selected = str(e.control.value)
            with SessionLocal() as db:
                treino_selected = db.query(Treino).filter_by(usuario_id=usuario_id, titulo=dropdown_selected).order_by(Treino.data.desc()).first()
            
                texto.value = dropdown_selected
            
                # if tem_Exercicios(treino=treino_selected):
                if treino_selected.exercicios_prescritos:
                    # Achatar a lista de exercícios e criar Texts
                    exercicios_series_repeticoes = [{'Nome':x.exercicio.nome, 'Séries': x.series, 'Repetições': x.repeticoes} for x in treino_selected.exercicios_prescritos]
                    for item in exercicios_series_repeticoes:
                        if not df_gifs[df_gifs['Arquivo'].str.contains(item['Nome'], case=False, na=False)].empty:
                            v = df_gifs[df_gifs['Arquivo'].str.contains(item['Nome'], case=False, na=False)]['Arquivo'].values
                            item['Gif'] = v[0]
                            col_lista_treinos.controls = [ft.Text(f"- {x['Nome']}".title(), size=16, weight='bold') for x in exercicios_series_repeticoes] or [ft.Text("Ainda não existe exrecícios para este treino!", color='red')]
                            row2.controls = [criar_card(nome=x['Nome'], series=x['Séries'], repeticoes=x['Repetições'], imagem_url=f"gifs/{x['Gif']}" if 'Gif' in x else None, page=page) 
                                                for x in exercicios_series_repeticoes]
                else:
                    exercicios_series_repeticoes = []
                
            page.update()

        # Dropdown populado com nomes dos treinos
        dropdown1 = ft.Dropdown(
            label='Selecione um treino',
            options=[ft.dropdown.Option(x) for x in sorted(set(nomes_treinos))],
            on_change=dropdown_chama,
            width=300,
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
                    expand=True,
                    controls=[
                        # Linha 1
                        ft.ResponsiveRow(
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                        # bgcolor=ft.Colors.BLUE_100,
                                        height=50,
                                        col={"xs": 12, "sm": 6, "md": 6},  # 100% em telas pequenas, 50% em médias, 33% em grandes
                                        content=ft.Text(f"Olá, {usuario.nome}!", size=24, weight="bold"),
                                    ),
                            ] 
                        ),
                        ft.Divider(),
                        # Linha 2
                        ft.ResponsiveRow(
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                        # bgcolor=ft.Colors.BLUE_100,
                                        height=150,
                                        col={"xs": 12, "sm": 5, "md": 5},  # 100% em telas pequenas, 50% em médias, 33% em grandes
                                        content=ft.Column(
                                                    controls=[
                                                        dropdown1
                                                ]
                                            )
                                        ),
                                ft.Container(
                                        # bgcolor=ft.Colors.BLUE_GREY_300,
                                        height=150,
                                        col={"xs": 12, "sm": 5, "md": 5},  # 100% em telas pequenas, 50% em médias, 33% em grandes
                                        content=ft.Column(
                                            expand=True,
                                            # scroll='auto',
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    controls=[
                                                        ft.Text('Exercícios', size=20, weight='bold'),
                                                        ft.Column(
                                                            expand=True,
                                                            scroll='auto',
                                                            controls=[col_lista_treinos],
                                                        ),
                                                        
                                                ]
                                            )
                                        ),
                            ] 
                        ),
                        ft.Divider(),
                        # Linha 3
                        ft.ResponsiveRow(
                            expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                        # bgcolor=ft.Colors.BLUE_GREY_300,
                                        height=250,
                                        col={"xs": 12, "sm": 10, "md": 10},  # 100% em telas pequenas, 50% em médias, 33% em grandes
                                        content=ft.Row(
                                            scroll='auto',
                                            controls=[row2]
                                            ), 
                                    ),
                            ] 
                        )
                    ]
                ),
            ],
            scroll='auto'
    )
    
    #############################
    def radio_item(e):
        radio_group.value = e.control.value
        page.update()
    radio_group = ft.RadioGroup(
        content=ft.Row([ft.Radio(value='Pré', label="Pré"), ft.Radio(value='Pós', label='Pós')]),
        on_change=radio_item
    )
    grid1 = ft.GridView(
        expand=True,
        # runs_count=8,
        max_extent=25,
        child_aspect_ratio=1.0,
        spacing=1,
        run_spacing=30,
    )
    # Adiciona 54 checkboxes ao grid
    checkboxes = [ft.Checkbox(label=f"{i} ", value=False) for i in range(1,54)]
    grid1.controls.extend(checkboxes)
    
    def slider_changed(e):
        slider1.value = e.control.value
        page.update()
        
    slider1 = ft.Slider(
        min=0, max=10, divisions=10, label="{value}", on_change=slider_changed
    )
    
    form_alerta = ft.AlertDialog(
        title=ft.Text("Formulário Enviado!"),
        content=ft.Text("Suas respostas foram enviadas"),
        alignment=ft.alignment.center,
        # on_dismiss=lambda e: print("Dialog dismissed!"),
        title_padding=ft.padding.all(12),
    )
    
    def cria_form_dor():
        return [
            ft.Text('Pré ou Pós Treino?',weight='bold', size=20, text_align='center'),
            radio_group,
            ft.Text('Quais Parte(s) do Corpo?', weight='bold', size=20, text_align='center'),
            ft.Text('Selecione partes para uma intensidade de dor', weight='bold', size=12, text_align='center'),
            grid1,
            ft.Text('Qual Intensidade da dor?', weight='bold', size=20, text_align='center'),
            ft.Text('Escala de 0 a 10', weight='bold', size=12, text_align='center'),
            slider1
        ]
    
    def limpa_form():
        radio_group.value = None
        slider1.value = 0
        for c in grid1.controls:
            c.value = False
        form1.update()
    #############################
    
    form1 = ft.Column(controls=cria_form_dor())
    resultado = ft.Text()
    resul_form_parte_corpo = []
    
    def enviar(e):
        usuario_id = page.session.get('usuario_id')
        resul_form_parte_corpo.clear()
        for cb in checkboxes:
            if cb.value:
                resul_form_parte_corpo.append(int(cb.label))
        pre_pos_treino = radio_group.value
        local = resul_form_parte_corpo
        intensidade = slider1.value

        if not pre_pos_treino or not local or not intensidade:
            resultado.value = "Preencha os campos!"
            resultado.color = "red"
        else:
            resultado.value = "Formulário enviado!"
            resultado.color = "green"
            with SessionLocal() as db:
                resposta = QuestionarioDor(
                usuario_id = usuario_id,
                pre_pos_treino = pre_pos_treino,
                local = local,
                intensidade = int(intensidade)
                )
                db.add(resposta)
                db.commit()
            page.open(form_alerta)
            # 🔁 Recriar os dropdowns para limpá-los visualmente
            limpa_form()

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
                        ft.Column(
                            expand=True,
                            controls=[
                                ft.ResponsiveRow(
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            col={"xs":12, "sm":6, "md":4},
                                            # bgcolor=ft.Colors.AMBER_500,
                                            content=ft.Text('Formulário de dor!', weight='bold', size=28, text_align='center'),
                                        )
                                        
                                    ]
                                ),
                                ft.ResponsiveRow(
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            col={"xs":12, "sm":8, "md":6},
                                            content=ft.Image(src='/imagem_corpo_numeros.jpeg', fit=ft.ImageFit.CONTAIN, )
                                        ),
                                        ft.Container(
                                            col={"xs":10, "sm":3, "md":5},
                                            content=ft.Column(
                                                expand=True,
                                                controls=[
                                                    form1,
                                                    enviar_button,
                                                    resultado
                                                ]
                                            )
                                        ),
                                        
                                    ]
                                ),
                                
                            ]
                        ),
                    ]
                )
                
    # # Atualiza largura dinamicamente ao redimensionar
    # def on_resize(e):
    #     page.controls[0].width = page.width
    #     page.update()
    # page.on_resize = on_resize
    
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
ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="assets")