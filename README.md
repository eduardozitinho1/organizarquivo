# 📁 Organizarquivo

**Sua pasta está uma bagunça? Deixa que ele organiza.**

Organizarquivo é uma CLI em Python que move arquivos para pastas por
tipo, com desfazer, preview e categorias customizáveis.

[![PyPI](https://img.shields.io/pypi/v/organizarquivo?style=flat-square)](https://pypi.org/project/organizarquivo/)
[![Python](https://img.shields.io/pypi/pyversions/organizarquivo?style=flat-square)](https://www.python.org/)
[![Downloads](https://img.shields.io/pypi/dm/organizarquivo?style=flat-square)](https://pypi.org/project/organizarquivo/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

---

## Instalação

    pip install organizarquivo

## Uso básico

    organizarquivo ~/Downloads

Ele pergunta antes de mover. Use `--dry-run` para ver o que faria sem
consequências.

## Comandos

    organizarquivo <pasta>            # organiza a pasta
    organizarquivo <pasta> -y         # organiza sem confirmar
    organizarquivo <pasta> --dry-run  # mostra o que faria
    organizarquivo <pasta> -r         # inclui subpastas
    organizarquivo <pasta> --stats    # mostra estatísticas ao final
    organizarquivo undo               # desfaz a última operação
    organizarquivo undo --list        # lista operações recentes

## Categorias

| Pasta | Exemplos |
|---|---|
| Documents | .pdf .docx .md .odt |
| Spreadsheets | .xlsx .csv .ods |
| Presentations | .pptx .key .odp |
| Images | .jpg .png .svg .heic .avif |
| Videos | .mp4 .mkv .webm .avi |
| Audios | .mp3 .flac .m4a .opus |
| Archives | .zip .rar .7z .tar.gz .zst |
| Code | .py .js .ts .cs .rs .go .html .css |
| Books | .epub .mobi .azw3 .djvu |
| Fonts | .ttf .otf .woff2 |
| 3D | .blend .obj .fbx .gltf |
| Design | .psd .ai .sketch .fig |
| Executables | .exe .msi .deb .rpm .dmg |
| Databases | .sqlite .db .mdb |
| Others | o resto |

## Desfazer

Cada execução grava um histórico em `~/.cache/organizarquivo/history/`.
Se algo foi para o lugar errado:

    organizarquivo undo

Reverte a última operação. Se um arquivo sumiu ou o local de origem já
está ocupado, o undo reporta a falha para aquele arquivo sem abortar os
outros.

## Configuração

Crie `~/.organizarquivo.toml`:

    [categories]
    "Trabalho" = [".docx", ".xlsx", ".pptx"]
    "Projetos" = [".blend", ".obj", ".fbx"]

    [exclude]
    patterns = ["*.tmp", "*.bak", "~*"]
    directories = ["Important", "Keep"]

    [behavior]
    confirm = true

Categorias customizadas **substituem** categorias de mesmo nome.
Exclusões se somam às da CLI.

## Segurança

- Não mexe em `.git`, `.venv`, `node_modules`, `__pycache__`, `target`,
  `build`, `dist` e outras pastas de infraestrutura.
- Sem `--recursive`, só mexe na raiz da pasta alvo. Subpastas preservadas.
- Arquivos com mesmo nome não se sobrescrevem: viram `foto (1).jpg`.
- `--dry-run` para ver antes sem consequências.

## Requisitos

- Python 3.9+ (3.11+ sem dependências extras; 3.9 e 3.10 usam `tomli`)

## Licença

MIT
