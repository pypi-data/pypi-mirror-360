
````markdown
# 🚀 hexgen — Gerador de Projetos com Arquitetura Hexagonal

`hexgen` (ou `hexo-cli`) é uma CLI Python para gerar rapidamente a estrutura base de um projeto com **arquitetura hexagonal**, seguindo boas práticas de organização de pastas e compatível com projetos `serverless`, `FastAPI`, `gRPC` e muito mais.

---

## 📦 Instalação

### Via PyPI (recomendado):

```bash
pip install hexgen
````
---

## ⚙️ Como usar

### Gerar um novo projeto:

```bash
hexgen meu_projeto ou .
```

Estrutura gerada:

```
meu_projeto/
├── README.md
├── requirements.txt
├── .gitignore
├── serverless.yaml
├── src/
│   ├── main.py
│   ├── application/
│   │   ├── routers/
│   │   └── use_cases/
│   ├── config/
│   │   ├── custom_config.py
│   │   └── dependency_start.py
│   ├── domain/
│   │   ├── entities/
│   │   ├── interfaces/
│   │   └── services/
│   ├── infra/
│   │   ├── repositories/
│   │   ├── clients/
│   │   └── dtos/
├── tests/
│   └── main.py
└── .github/
    └── workflows/
        └── aws_deploy.yml
```

Todos os diretórios dentro de `src/` recebem automaticamente arquivos `__init__.py`.

---

## 📁 Templates

Os arquivos gerados vêm de templates internos que incluem:

* `main.py` de entrada
* `serverless.yaml` já pronto para AWS Lambda
* `dependency_start.py` e `custom_config.py` para configurações
* `aws_deploy.yml` para CI/CD com GitHub Actions

---

## 🧑‍💻 Desenvolvimento local

Clone este repositório e instale em modo desenvolvimento:

```bash
git clone https://github.com/seunome/hexo-cli.git
cd hexo-cli
pip install -e .
```

Agora você pode rodar:

```bash
hexgen nome_do_projeto
```

---

## 📤 Publicar no PyPI (manutenção)

Para empacotar:

```bash
python -m build
```

Para subir:

```bash
twine upload dist/*
```

> 🔁 Lembre-se de aumentar a versão no `pyproject.toml` a cada novo upload.

---

## 🤝 Contribuição

Sinta-se à vontade para abrir issues, pull requests ou sugestões de melhoria!


## 📃 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
