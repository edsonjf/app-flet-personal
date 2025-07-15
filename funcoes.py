from models import SessionLocal, Treino
import pandas as pd
import os

import flet as ft

dados = {
    'Arquivo': os.listdir('assets'),
}
df_gifs = pd.DataFrame(dados)

# with SessionLocal as db:
def obter_gifs(id:int, db): 
    index = []
    for item in db.query(Treino).filter_by(usuario_id=id):
        for exercicio in item.exercicios:
            print(exercicio.nome)
            filtro = df_gifs['Arquivo'].str.contains(exercicio.nome, case=False, na=False)
            if not df_gifs[filtro].empty:
                ids = df_gifs[filtro].index.tolist()
                index.extend(ids)
    gifs = df_gifs.loc[index]['Arquivo'].values.tolist()
    return gifs

# def criar_card(nome: str, descricao: str, imagem_url: str) -> ft.Card:
def criar_card(nome: str, series: int, repeticoes:int, imagem_url: str, page) -> ft.Card:
    return ft.Card(
        col={"xs": 10, "sm": 6, "md": 4},
        # elevation=4,
        content=ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            padding=10,
            content=ft.Column([
                ft.Row(
                    expand=2,
                    # scroll='auto',
                    controls=[ft.Image(
                        src=imagem_url,
                        # width=page.width * 0.2,
                        # height=page.height * 0.2,
                        fit=ft.ImageFit.CONTAIN
                        ),
                    ],
                    
                ),
                ft.Column(
                    expand=1,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(nome, style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.Text(f"Séries: {series}", size=12, italic=True),
                        ft.Text(f"Repetições: {repeticoes}", size=12, italic=True)
                    ],
                )
                
            ]),
        ),
        # width=page.width * 0.2, 
    )
