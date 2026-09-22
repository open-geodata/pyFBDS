# _Getting Started_

## Como Instalar?

O pacote está dispnível no [PyPI](https://pypi.org/project/pyFBDS).

```shell
pip3 install pyFBDS
```

<br>

---

## Como Usar?

Abaixo é apresentado uma forma simples de utilizar o pacote. Para mais exemplos, consultar o _script_ [01_post.ipynb](./docs/scripts/post/01_post.ipynb).

```python
# Importa pacote
from pyFDBS.post import FBDS

# Instancia FBDS
fbds = FBDS(output_path=output_path)

# Faz Download dos Dados para output_path
fbds.download(municipality='SANTOS', uf='SP')

# Lê dados espaciais em formato geodataframe
gdf = fbds.read_data(municipality='SANTOS', uf='SP', layer="APP_USO")
```
