# pyFBDS

[![Repo](https://img.shields.io/badge/GitHub-repo-blue?logo=github&logoColor=f5f5f5)](https://github.com/open-geodata/pyFBDS)
[![PyPI - Version](https://img.shields.io/pypi/v/pyFBDS?logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/pyFBDS/)<br>
[![Read the Docs](https://img.shields.io/readthedocs/pyfbds/latest?logo=ReadTheDocs&label=Read%20The%20Docs)](https://pyfbds.readthedocs.io/)
[![Publish Python to PyPI](https://github.com/open-geodata/pyFBDS/actions/workflows/publish-to-pypi-uv.yml/badge.svg)](https://github.com/open-geodata/pyFBDS/actions/workflows/publish-to-pypi-uv.yml)

Pacote e _scripts_ para obter dados espaciais do [**repositório público de mapas e _shapefiles_ para _download_**](https://geo.fbds.org.br/) disponibilizados pela [Fundação Brasileira para o Desenvolvimento Sustentável (FBDS)](https://www.fbds.org.br).

Veja mais na documentação:

> [https://pyFBDS.readthedocs.io](https://pyFBDS.readthedocs.io/)

<br>

![qgis](docs/assets/imgs/qgis.png)

<br>

---

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

<br>

---

## _TODO_

1. Ajustar os tipos de arquivos (Pontos, _Polylines_, _Polygons_), visto que na lista de arquivos surgiu uma feição curiosa:
   1. _RIOS_DUPLOS.shp_
   2. _RIOS*DUPLOS*.shp_
   3. _RIOS_DUPLOS_POL.shp_
