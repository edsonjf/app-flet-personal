import flet as ft
import os
from models import Usuario, SessionLocal, Treino

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
        
    def home():
        usuario_id = page.session.get('usuario_id')
        with SessionLocal() as db:
            usuario = db.query(Usuario).filter_by(id=usuario_id).first()
        return ft.View(
            "/",
            controls=[
                ft.AppBar(
                    title=ft.Text("Página Inicial", weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.BLUE_GREY_700, 
                    center_title=True,
                    actions=[
                        ft.ElevatedButton('Treinos', on_click= lambda _: page.go('/treinos')),
                        ft.ElevatedButton("Sair", on_click=lambda _: page.go('/login')),
                    ]
                    ),
                ft.Column([
                    ft.Text(f"Olá {usuario.nome}"),
                    ft.Text(f"Status da sessão: {page.session.get('loggedIn')}"),
                    ft.Text(f"{usuario.email}")
                    ]
                ),
                ft.Text('HOme'),
            ]
        )
    
    def page_treinos():
        usuario_id = page.session.get('usuario_id')
        with SessionLocal() as db:
            treinos = db.query(Treino).filter_by(usuario_id=usuario_id).all()
        treinos_existentes = [ft.Text(x.nome) for x in treinos]
        exercicios = [x.exercicios for x in treinos]
        gifs = [gif for gif in os.listdir('imagens') if any(exercicio[2:4] in gif for exercicio in exercicios)]
        return ft.View(
            "/treinos",
            controls=[
                ft.AppBar(
                    title=ft.Text("Página Treino", weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.BLUE_GREY_700, 
                    center_title=True,
                    actions=[
                        ft.ElevatedButton('Início', on_click=lambda _: page.go('/')),
                        ft.ElevatedButton("Sair", on_click=lambda _: page.go('/login'))
                    ],
                    ),
                ft.Column([
                    ft.Text(f"ID usuário {usuario_id}"),
                    # ft.ElevatedButton('Logout', on_click=logout),
                    ft.Text(f"Status da sessão: {page.session.get('loggedIn')}")
                    ]
                ),
                ft.Text('Treinos'),
                ft.Container(
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_500),  # cor verde com 20% de opacidade
                    height=400,
                    expand=True,
                    content=ft.Column(
                        controls=[
                            # Primeira linha
                            ft.Row(
                                controls=[
                                    ft.Text('Linha 1'),

                                    # Container dentro da Row, com fundo vermelho claro
                                    ft.Container(
                                        padding=20,
                                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.RED),
                                        content=ft.Row(
                                            controls=[
                                                ft.Text("Subitem A"),
                                                ft.Text("Subitem B"),
                                            ]
                                        )
                                    ),
                                    ft.Container(
                                        padding=20,
                                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.RED),
                                        content=ft.Row(
                                            controls=[
                                                ft.Text("Subitem C"),
                                                ft.Text("Subitem D"),
                                            ]
                                        )
                                    )
                                ],
                                # expand=1
                                # alignment="center",  # pode ser usado para ajustar o alinhamento
                            ),

                            # Segunda linha
                            ft.Row(
                                controls=[
                                    ft.Text('Linha 2'),
                                    ft.Text(exercicios),
                                    
                                    ft.Container(
                                        content=ft.Image(
                                        src='imagens\Agachamento 1.gif',
                                        fit=ft.ImageFit.CONTAIN
                                        ),
                                        expand=1
                                    ),
                                    # ft.Container(
                                    #     content=ft.Image(
                                    #     src='imagens\Avanco.gif',
                                    #     fit=ft.ImageFit.CONTAIN
                                    #     ),
                                    #     expand=1
                                    # ),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Image(src=f"imagens/{item}", fit=ft.ImageFit.CONTAIN) for item in gifs
                                        ],
                                        expand=1)
                                    ),
                                    
                                ],
                            ),
                        ]
                    )
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
        elif page.route == '/treinos':
            page.views.append(page_treinos())
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