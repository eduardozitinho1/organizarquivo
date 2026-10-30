# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
versionamento em [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.1.3] - 2026-10-30

### Corrigido

- Pastas ocultas e de infraestrutura (`.git`, `.venv`, `node_modules`,
  `__pycache__`, `target`, `build`, `dist`, e outras) nao sao mais
  varridas. Rodar `organizarquivo` na raiz de um repositorio git nao
  destroi mais o `.git`.
- Arquivos dentro de subpastas nao sao mais movidos por padrao. Apenas
  os arquivos da raiz da pasta alvo sao organizados.
- Arquivos dentro de uma pasta de categoria nao sao reorganizados quando
  o comando roda pela segunda vez.

### Adicionado

- Confirmacao interativa antes de mover arquivos. `-y` / `--yes` pula.
- `--dry-run` mostra o que seria movido, sem mover nada.
- Aviso em stderr quando a pasta alvo e um repositorio git.

## [0.1.2] - 2026-10-30

### Alterado

- Metadata do pacote migrada para SPDX: `license = "MIT"` e
  `license-files = ["LICENSE"]` no `pyproject.toml`.
- Classifier `License :: OSI Approved :: MIT License` removido. A
  expressao SPDX ja cobre essa informacao.
- `setuptools` minimo passou para `>=77`, a primeira versao que aceita
  o formato SPDX.

### Notas

- Sem mudanca de comportamento. `uv build` roda sem warnings de
  deprecacao, e o `License-Expression` aparece corretamente no
  `METADATA` do wheel.

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
