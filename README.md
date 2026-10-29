# SalesInsight PY

Projeto de análise de dados de vendas desenvolvido em Python.

## Funcionalidades

- Leitura e limpeza de dados de vendas em CSV.
- Tratamento de datas e preparação dos dados.
- Cálculo de indicadores comerciais.
- Análise de receita, produtos, categorias e regiões.
- Geração automática de quatro gráficos.
- Exportação de métricas e resultados.

## Indicadores

O projeto calcula indicadores como:
- Quantidade de transações válidas.
- Receita total.
- Quantidade total vendida.
- Ticket médio por transação.
- Quantidade de clientes identificados.

## Tecnologias

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn

## Estrutura do projeto

```text
SalesInsight_PY/
├── main.py
├── vendas.csv
├── README.md
├── requirements.txt
├── .gitignore
└── outputs/
    ├── graficos/
    ├── estatisticas_gerais.json
    ├── metricas_por_mes.csv
    └── segmentacao_clientes.csv
```

## Como executar

1. Instale o Python 3.10 ou superior.
2. Instale as dependências:

   pip install -r requirements.txt

3. Coloque o arquivo vendas.csv na pasta do projeto.
4. Execute:

   python main.py

Os resultados são exportados para a pasta outputs.

## Observações

O arquivo vendas.csv utilizado neste projeto é uma base de
análise. Antes de utilizar dados reais, verifique a qualidade,
a autorização de uso e a proteção dos dados pessoais.
