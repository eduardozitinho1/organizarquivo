
<div align="center">

# 📁 Organizarquivo

**Sua pasta está uma bagunça? Deixa que ele organiza.**

Organizarquivo é um pequeno programa feito em Python que coloca seus arquivos em pastas, de acordo com o tipo de cada um.

[![PyPI](https://img.shields.io/pypi/v/organizarquivo?style=flat-square)](https://pypi.org/project/organizarquivo/)
[![Python](https://img.shields.io/pypi/pyversions/organizarquivo?style=flat-square)](https://www.python.org/)
[![Downloads](https://img.shields.io/pypi/dm/organizarquivo?style=flat-square)](https://pypi.org/project/organizarquivo/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

---

## O que ele faz?

Sabe aquela pasta Downloads cheia de PDFs, imagens, músicas, vídeos e arquivos que você nem lembra de onde vieram?

O Organizarquivo resolve essa bagunça. Você informa uma pasta, ele olha os arquivos que estão lá e coloca cada um em seu devido lugar.

Sem precisar ficar arrastando arquivo por arquivo.

## Instalação

Você pode instalar diretamente pelo pip:

```bash
pip install organizarquivo
```

## Como usar

Depois de instalar, basta abrir o terminal e executar:

```bash
organizarquivo ~/Downloads
```

Troque `~/Downloads` pelo caminho da pasta que deseja organizar.

Pronto! O programa cuida do resto.

## Onde cada arquivo vai parar?

O Organizarquivo separa os arquivos nestas pastas:

| Pasta | Tipos de arquivo |
|---|---|
| Documents | `.pdf`, `.docx`, `.doc`, `.txt` |
| Images | `.jpeg`, `.jpg`, `.png` |
| Videos | `.mp4`, `.mkv`, `.mov` |
| Audios | `.wav`, `.mp3` |
| Spreadsheets | `.xlsx`, `.xls`, `.csv` |
| Others | Todo o restante |

Se o programa encontrar um arquivo que não conhece, ele não fica perdido: vai para `Others`.

## Um exemplo

Imagine que sua pasta esteja assim:

```text
Downloads/
├── foto.jpg
├── trabalho.pdf
├── musica.mp3
├── planilha.xlsx
├── filme.mp4
└── arquivo.zip
```

Depois de executar o Organizarquivo:

```text
Downloads/
├── Documents/
│   └── trabalho.pdf
├── Images/
│   └── foto.jpg
├── Audios/
│   └── musica.mp3
├── Spreadsheets/
│   └── planilha.xlsx
├── Videos/
│   └── filme.mp4
└── Others/
    └── arquivo.zip
```

Bem melhor, né?

## Algumas informações

- Funciona com Python 3.6 ou superior.
- Não precisa instalar outras bibliotecas.
- Funciona no Windows, Linux e macOS.
- Também procura arquivos dentro das subpastas.
- Não exclui arquivos intencionalmente.
- Reconhece extensões mesmo quando estão escritas em letras maiúsculas.

**Atenção:** o programa movimenta os arquivos de verdade. Antes de organizar uma pasta importante, recomendamos fazer uma cópia de segurança.

## Perguntas frequentes

<details>
<summary>Ele copia ou move os arquivos?</summary>

Ele move. Os arquivos saem de onde estavam e vão para as pastas correspondentes.

</details>

<details>
<summary>E se o arquivo não tiver uma extensão conhecida?</summary>

Ele vai para a pasta `Others`.

</details>

<details>
<summary>Preciso saber programar para usar?</summary>

Não! Basta instalar e executar o comando no terminal.

</details>

<details>
<summary>Posso usar em uma pasta com muitos arquivos?</summary>

Sim. O programa consegue percorrer pastas com muitos arquivos, embora o tempo necessário dependa do computador e do armazenamento.

</details>

## Contribuições

Encontrou algum problema ou teve uma ideia interessante?

Fique à vontade para abrir uma [issue](../../issues) ou enviar um [pull request](../../pulls).

Toda ajuda é bem-vinda!

## Licença

Este projeto é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para saber mais.

---

<div align="center">

Feito com Python para deixar suas pastas um pouco menos caóticas.

**Organizarquivo**

</div>
