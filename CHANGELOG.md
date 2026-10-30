# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
versionamento em [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.1.1] - 2026-10-30

### Corrigido

- Arquivos com mesmo nome em pastas diferentes nao se sobrescrevem mais.
  Quando `Images/foto.jpg` ja existe, o proximo arquivo vai como
  `foto (1).jpg`, preservando o original.
- A pasta `Others` so e criada quando existe pelo menos um arquivo para ela.
- Removida a exclusao fixa do arquivo `main.py`. Agora ele e organizado
  como qualquer outro.

### Alterado

- Projeto movido para layout `src/organizarquivo/`.
- CLI retorna exit code 0 em sucesso e 1 em erro.
- Mensagem de uso vai para stderr.
- `requires-python` ajustado para `>=3.9`.

## [0.1.0] - 2026-10-29

### Adicionado

- Versao inicial.
