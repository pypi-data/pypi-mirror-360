# Meu Tabplot Interativo Python

Um pacote Python para gerar gráficos de tabplot interativos, inspirados na funcionalidade do `tabplot` do R. Visualize a distribuição e o comportamento de suas variáveis ao longo de um eixo de ordenação, com suporte para dados numéricos e categóricos.

## Instalação

Você pode instalar `meu-tabplot-library` (ou o nome que você escolher para o seu pacote) diretamente via pip:

```bash
pip install meu-tabplot-library # <--- ATENÇÃO: Mude 'meu-tabplot-library' para o NOME REAL do seu pacote no PyPI

Como Usar
Aqui está um exemplo básico de como utilizar o pacote para gerar um tabplot:

import pandas as pd
import numpy as np # Necessário para o exemplo de dados dummy

# Importa as funções do seu pacote.
# <--- ATENÇÃO: Mude 'meu_tabplot_lib' para o NOME EXATO DA SUA PASTA DE PACOTE (ex: 'seupacote')
from meu_tabplot_lib.binning import simulate_tabplot_binning, plot_tabplot_interactive 

# 1. Carregar seus dados (exemplo com um DataFrame dummy)
# df = pd.read_excel("caminho/para/seus_dados.xlsx")
# Se você tiver um arquivo CSV, use: df = pd.read_csv("caminho/para/seus_dados.csv")
# Ou crie um DataFrame de exemplo para testar:
data = {
    'ID_Cliente': range(1, 1001),
    'Valor_Compra': np.random.rand(1000) * 1000,
    'Idade': np.random.randint(18, 70, 1000),
    'Regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste'], 1000),
    'Assinante': np.random.choice([True, False, np.nan], 1000, p=[0.45, 0.45, 0.1]),
    'Categoria_Produto': np.random.choice(['Eletronicos', 'Roupas', 'Alimentos', 'Servicos', 'Outros'], 1000)
}
df_exemplo = pd.DataFrame(data)

# 2. Definir a coluna para ordenação
# Escolha uma coluna numérica do seu DataFrame para ordenar os bins
sort_column = "Valor_Compra" 

# 3. Preparar os dados para o tabplot usando a função de binning
# nbins: Número de fatias (bins) em que o dataset será dividido
# sort_col: A coluna pela qual o dataset será ordenado
# decreasing: True para ordenar decrescentemente (do maior para o menor), False para crescentemente
# max_levels: Limite de categorias para colunas categóricas (categorias menos frequentes serão agrupadas em 'Outros')
binned_data, _, _ = simulate_tabplot_binning(
    df_exemplo,
    nbins=100,
    sort_col=sort_column,
    decreasing=False, # Use True para ordenação decrescente (ex: do cliente de maior compra para o de menor)
    max_levels=10
)

# 4. Gerar e exibir o tabplot interativo
# title: O título que aparecerá no topo do seu gráfico
plot_tabplot_interactive(binned_data, title=f"Tabplot do Dataset (Ordenado por {sort_column})")

Contribuição
Contribuições são bem-vindas! Se você tiver sugestões, encontrar problemas ou quiser adicionar novas funcionalidades, por favor, abra uma issue ou pull request no repositório GitHub do projeto.

Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
