# pyFBDS

[![Repo](https://img.shields.io/badge/GitHub-repo-blue?logo=github&logoColor=f5f5f5)](https://github.com/open-geodata/pyFBDS)
[![PyPI - Version](https://img.shields.io/pypi/v/pyfbds?logo=pypi&label=PyPI&color=blue)](https://pypi.org/project/pyfbds/)<br>
[![Read the Docs](https://img.shields.io/readthedocs/pyFBDS?logo=ReadTheDocs&label=Read%20The%20Docs)](https://pyFBDS.readthedocs.io/)
[![Publish Python to PyPI](https://github.com/michelmetran/pyFBDS/actions/workflows/publish-to-pypipoetry.yml/badge.svg)](https://github.com/michelmetran/pyFBDS/actions/workflows/publish-to-pypipoetry.yml)

_Scripts_ para obter dados espaciais do [**repositório público de mapas e _shapefiles_ para _download_**](https://geo.fbds.org.br/). Veja mais na documentação:

> [https://pyFBDS.readthedocs.io/](https://pyFBDS.readthedocs.io/)

<br>

---

## Como Instalar?

```shell
pip3 install pyFBDS
```

<br>

---

## Como Usar?

```shell
# Importa pacote
import pyFBDS

# Instancia Objeto
fbds = pyFBDS.Repo(output_path='.')

# Chama o método
fbds.get_municipio(id_ibge=353243)
```
