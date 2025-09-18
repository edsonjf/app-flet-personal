from models import SessionLocal, Treino, TreinoRealizado
import pandas as pd
import os

import flet as ft

dados = {
    'Arquivo': os.listdir('assets/gifs'),
}
df_gifs = pd.DataFrame(dados)

def obter_gifs(id:int, db): 
    index = []
    for item in db.query(Treino).filter_by(usuario_id=id).all():
        for exercicio in item.exercicios_prescritos:
            index.append(exercicio.id)
    gifs = df_gifs.loc[index]['Arquivo'].values.tolist()
    return gifs

def criar_card(nome: str, series: int, repeticoes:int, tempo:float | None, peso:float | None, intervalo:float | None,
               usuario_id, treino_id, exercicio_id,
               botao_play, imagem_url: str, page) -> ft.Card:
    
    controle = ft.Row(
        controls=[
            ft.IconButton(ft.Icons.REMOVE, on_click=lambda e: diminuir(e, page)),
            txt_number,
            ft.IconButton(ft.Icons.ADD, on_click=lambda e:acrescentar(e, page)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    form = ft.AlertDialog(
        title=ft.Text("Registrar Exercício"),
        content=ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text('Quantas séries:'),
                        
                        controle
                    ]
                ), 
                ft.Column(
                    [
                        coluna1
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    width=300,
                    scroll=ft.ScrollMode.AUTO
                ),
                ft.ElevatedButton("Salvar Série", on_click=lambda e: salva_fecha_form(e))
            ]
        ),
        alignment=ft.alignment.center,
        title_padding=ft.padding.all(25),
    )
    
    def salva_fecha_form(e):
        salvar_resultados(e, usuario_id=usuario_id, treino_id=treino_id, exercicio_id=exercicio_id, page=page)
        form.open = False
        page.update()
    
    def abre_limpa_form(e):
        coluna1.controls.clear()
        txt_number.value = 0
        page.open(form)
        
    icon_button = ft.IconButton(
        icon=ft.Icons.SAVE,
        icon_color= ft.colors.LIGHT_GREEN_400,
        icon_size=40,
        tooltip="Salvar Séries",
        # on_click=lambda e: page.open(form),
        on_click=lambda e: abre_limpa_form(e=e),
        # disabled= True,
        # visible=True
    )
        
    return ft.Card(
        width=None,
        height=None,
        expand=True, 
        col={"xs": 8, "sm": 6, "md": 4},
        content=ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        controls=[ft.Image(
                            src=imagem_url,
                            error_content=ft.Text("Imagem não encontrada", color="red"),
                            height=200,
                            fit=ft.ImageFit.CONTAIN, 
                            expand=1, 
                            ),
                            icon_button
                        ],
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            ft.Divider(),
                            ft.Text(nome.title(), style=ft.TextThemeStyle.TITLE_MEDIUM, no_wrap=False, max_lines=2),
                            ft.Divider(),
                            ft.Row(
                                expand=True,
                                controls=[
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            ft.Text(f"Séries: {series}", size=12, italic=True),
                                            ft.Text(f"Repetições: {repeticoes}", size=12, italic=True) if repeticoes is not None else ft.Text(f"Tempo: {tempo} minuto(s)", size=12, italic=True),
                                        ]
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            ft.Text(f"Peso: {peso} Kg", size=12, italic=True) if peso is not None else ft.Text(),
                                            ft.Text(f"Intervalo: {intervalo} minuto(s)", size=12, italic=True) if intervalo is not None else ft.Text()
                                        ]
                                    )
                                ]
                            ),
                            
                        ]
                    ),
                    
                )
            ],
            
    ),
)

txt_number = ft.TextField(value="0", width=50, text_align=ft.TextAlign.CENTER, read_only=True,
                          keyboard_type="number", input_filter=ft.NumbersOnlyInputFilter(),)
coluna1 = ft.Column()
resultados_exibidos = ft.Column() 

def parse_float(valor):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return 0.0  # ou outra lógica que você preferir

def parse_int(valor):
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0

def acrescentar(e, page):
    txt_number.value = str(int(txt_number.value) + 1)
    atualizar_coluna1(e)
    page.update()

def diminuir(e, page):
    txt_number.value = str(int(txt_number.value) - 1) if int(txt_number.value) > 0 else '0'
    atualizar_coluna1(e)
    page.update()

sliders = []
cargas = []
tempos = []
    
def atualizar_coluna1(e=None):
    try:
        qtd = int(txt_number.value)
    except:
        qtd = 0
        
    coluna1.controls.clear()
    resultados_exibidos.controls.clear()
    sliders.clear()
    cargas.clear()
    tempos.clear()
    
    for i in range(qtd):
        slider = ft.Slider(min=0, max=20, divisions=20, label="{value}")
        carga = ft.TextField(label="Carga", width=80, input_filter=ft.NumbersOnlyInputFilter(), keyboard_type="number", autofocus=True)
        tempo = ft.TextField(label="Tempo", width=80, input_filter=ft.NumbersOnlyInputFilter(), keyboard_type="number", autofocus=True)

        # Armazena os widgets
        sliders.append(slider)
        cargas.append(carga)
        tempos.append(tempo)
        coluna1.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(f"{i+1}ª série - Repetições:"),
                                slider
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                carga,
                                tempo
                            ]
                        )
                    ]
                )
            )
        )
    # .update()
    

def salvar_resultados(e, usuario_id:int,
                        treino_id:int,
                        exercicio_id:int, page):
    with SessionLocal() as session:
        for i in range(len(sliders)):
            serie = i + 1
            repeticoes = parse_int(sliders[i].value)
            carga = parse_float(cargas[i].value)
            tempo = parse_float(tempos[i].value)
            try:
                realizado = TreinoRealizado(
                        usuario_id =usuario_id,
                        treino_id=treino_id,
                        exercicio_id=exercicio_id,
                        # exercicio_nome='teste',
                        serie=serie,
                        repeticoes=repeticoes,
                        tempo=tempo,
                        carga=carga,
                    )
                session.add(realizado)
                session.commit()
                print('commit')
            except Exception as ex:
                session.rollback()
                print("Erro ao salvar:", ex)
    resultados_exibidos.controls.clear()  # Limpa antes de mostrar novamente
    # form.open = False

    page.update()

# botao_salvar = ft.ElevatedButton("Salvar Séries", on_click=lambda e: salvar_resultados(e,))
atualizar_coluna1()

