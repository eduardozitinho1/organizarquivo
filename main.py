from pathlib import Path
import shutil
import sys


def main():
    def not2args():
        raise Exception(
            "É necessário passar exatamente 1 argumento (o diretório alvo). Exemplo: python main.py meu_diretorio"
        )

    if len(sys.argv) != 2:
        not2args()

    dir_alvo = Path(sys.argv[1])
    if not dir_alvo.exists() or not dir_alvo.is_dir():
        raise Exception(f"O diretório '{dir_alvo}' não existe ou não é uma pasta válida.")

    pastas_destino = {
        "Documents": [".pdf", ".docx", ".doc", ".txt"],
        "Images": [".jpeg", ".jpg", ".png"],
        "Videos": [".mp4", ".mkv", ".mov"],
        "Audios": [".wav", ".mp3"],
        "Spreadsheets": [".xlsx", ".xls", ".csv"],
    }
    pasta_others = dir_alvo / "Others"

    for nome_pasta in pastas_destino.keys():
        (dir_alvo / nome_pasta).mkdir(parents=True, exist_ok=True)
    pasta_others.mkdir(parents=True, exist_ok=True)

    arquivos_para_mover = [
        f for f in dir_alvo.rglob("*") if f.is_file() and f.name != "main.py"
    ]

    print(f"Foram encontrados {len(arquivos_para_mover)} arquivos para mover!")

    ext_map = {
        ext: pasta for pasta, extensoes in pastas_destino.items() for ext in extensoes
    }

    contagem_categorias = {pasta: 0 for pasta in pastas_destino.keys()}
    contagem_categorias["Others"] = 0

    counter = 0

    for arquivo in arquivos_para_mover:
        if arquivo.parent.name in pastas_destino or arquivo.parent.name == "Others":
            continue

        ext = arquivo.suffix.lower()

        if ext in ext_map:
            categoria_atual = ext_map[ext]
            destino = dir_alvo / categoria_atual / arquivo.name
        else:
            categoria_atual = "Others"
            destino = pasta_others / arquivo.name

        try:
            shutil.move(str(arquivo), str(destino))
            counter += 1
            contagem_categorias[categoria_atual] += 1
        except Exception as e:
            print(f"Erro ao mover {arquivo.name}: {e}")

    print(f"Foram organizados {counter} arquivos!")
    print("Arquivos por categoria:")

    for categoria, total in contagem_categorias.items():
        if total > 0:
            print(f"  - {categoria}: {total} arquivo(s)")

    print("✨ Organização concluída com sucesso!")


if __name__ == "__main__":
    main()
