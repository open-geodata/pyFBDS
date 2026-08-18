# Abordagens

<br>

---

## Primeira Abordagem (_ruim e, portanto, descontinuada_)

A concepção empregada foi obter a lista dos arquivos em formato tabular (_.csv_) para, posteriormente, fazer o _download_.

Usando o [_./scripts_/**01_get_data.ipynb**](scripts/01_get_data.ipynb), foi utilizada a seguinte concepção: Para criar a lista de arquivos, fiz com auxílio do _selenium_. Com o _driver_ eram realizados os seguintes procedimentos:

1. Listar todos as **Subpastas** e **Arquivos** de um diretório raiz;
2. Para cada **Subpasta** encontrada, entra-se nela, e repetir o procedimento de listar **Arquivos**, retornando para a pasta anterior ao final
3. Fazia isso de modo em _loop_, utilizando uma função recursiva.
4. A cada iteração, todas as URLs apresentadas eram colecionadas em um tabela _.csv_.

<br>

![Abordagem_1](./assets/imgs/abordagem_1.gif)

<br>

Uma vez com todos os links, foi realizado o download usando o JDownloder, com arquivo [_scripts_/**03_download_list_files.ipynb**](scripts/03_download_list_files.ipynb)

<br>

---

### Segunda Abordagem (_melhor!!_)

A partir do [diretório do Estado de São Paulo](https://geo.fbds.org.br/SP/), com 645 pastas (uma para cada município), foi realizado o _download_ da pasta, resultando em 645 arquivos _.tar_. Isso foi feito com o arquivo [_./scripts_/**01_get_data.ipynb**](scripts/01_get_data.ipynb). A ideia era:

1. Listar todos as **Subpastas** (que represetam os municípios) de um diretório raiz;
2. Usando os conceitos de [_ActionChains_](https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.action_chains.html), passar o mouse sobre a pasta e clicar nela.
3. Clicar no botão "Fazer Download".

<br>

![Abordagem_2](./assets/imgs/abordagem_2.gif)

<br>

Após isso, com uso do [_scripts_/**02_adjust_data.ipynb**](scripts/02_adjust_data.ipynb), foram feitos os seguintes procedimentos:

1. Listar todos os arquivos _shapefile (.shp)_ que estão dentro dos arquivos _.tar_, sem descompactar!
2. Criar uma tabela com essa lista de arquivos.
3. Ajustar essa tabela, agregando diversas informações para re-criar os caminhos para o arquivo.
4. Criar cententas de arquivos temporários (com auxílio da bibliotenca [_tempfile_](https://docs.python.org/3/library/tempfile.html)), com o mesmo padrão de nome, evitando a necessidade de descompactar os arquivos _.tar_
5. Listar os arquivos _fake shapefile_ e ajusta-los, para que direcionem ao arquivo dentro do _.tar_
6. Testar e leitura dos arquivos pelo geopandas, conectar e salvar... para cada feição.


