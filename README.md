# Dashboard - BI de Acompanhamento de Desempenho do Setor Comercial

## O Problema de Negócio

Durante minha atuação como Gestor Financeiro, identifiquei que o acompanhamento das metas e comissões do time comercial lidava com problemas operacionais:

- Dados Não Estruturados: Cada vendedor utilizava planilhas, textos com formatações e organização próprias, dificultando a junção e análise dessas informações.

- Visão Fragmentada: Impossibilidade de consolidar o resultado geral da equipe em tempo hábil.

- Trabalho Manual: Calcular a conversão e separar, classificar e relacionar as comissões era um processo demorado e propenso a erros.

##  A Solução Técnica (ETL & BI)

A princípio, elaborei um modelo de planilha no google sheets com um simples quadro de visualização dos valores mais importantes, de modo que a forma de registro de metas, vendas, propostas e negociações fosse padronizado entre os membros do setor comercial.

<img width="1114" height="556" alt="image" src="https://github.com/user-attachments/assets/982c8ba5-9913-47a2-a6e7-2770700ef520" />



Entretanto, ainda não era a solução ideal, pois o acompanhamento dos registros e do desempenho da equipe ainda era descentralizado e exigia uma união e organização das planilhas de cada vendedor.
Com isso em mente, e com os novos conhecimentos que venho desenvolvendo durante a graduação, pensei em criar algo simples para otimizar esse processo:
Desenvolvi um script em Python que automatiza o processo, com a leitura da planilha pura, a limpeza do formato dos dados, a extração até a plotagem do gráfico para a diretoria:

 ### Extração e Tratamento (Pipeline ETL)

O script app.py funciona com uma função de limpeza que atua da seguinte forma:

* Busca Dinâmica: O código escaneia os arquivos .csv (download das planilhas) linha a linha até encontrar a informação "DATA" (que é, de fato, o início das iformações úteis), ignorando todo o quadro visual do topo da planilha do Google Sheets.

* Limpeza de Dados: Converte as strings de moedas (ex: R$ 1.250,50) para padrão numérico de máquina (1250.50), converte as datas (Datetime) e, por segurança, uma verificação de codificação do arquivo (pode estar em latin e acabar dando conflito com o padrao americano que é padrao do python).

* União: Mesclagem automática de múltiplos arquivos de vendedores em um único DataFrame do Pandas.

### Dashboard e Visualização (Streamlit + Plotly)

Construí uma interface web simples, utilizando o Streamlit, que facilita muito o processo de criação da interface web. Coloquei recursos como:

 * Filtros Dinâmicos: Cruzamento de dados por Status (fechado, negociando ou recusado) e Vendedor em tempo real.

 * KPIs Estratégicos: Faturamento Fechado, Propostas e orçamentos em Aberto (Negociações), Total de Leads e Taxa de Conversão.

 * Inteligência Visual: Gráficos interativos em Plotly para acompanhamento de Meta e do que já foi alcançado e distribuição das oportunidades e abordagens comerciais.

 * Informações Detalhadas: Ao final do dashboard, o usuário tem acesso aos dados puros utilizados, separados por vendedor, data, cliente, valor e status, organizados em forma de tabela simples.

   ### Resultado

   <img width="1310" height="592" alt="image" src="https://github.com/user-attachments/assets/9c95f9ad-a0bc-428e-98fb-8e41d7098e47" />

 >  _OBS: Dados fictícios, alterados para sigilo da empresa_

### Ferramentas utilizadas:

* Pandas: Utilizado para manipulação dos arquivos .csv e pelos recursos que permitem trabalhar e converter os formatos "sujos" das informações brutas para um formato apropriado para a aplicação.

* Streamlit: Framework utilizado para desenvolver o painel visual. O StreamLit facilita muito a criação do front-end. Ele permitiu criar uma interface com filtros na sidebar e os cartões dos indicadores de desempenho sem a necessidade de marcar o html e estilizar com css do zero.

* Plotly Express: Biblioteca para Business Intelligence visual. Possui recurso para a criação e plotagem dos gráficos de maneira bem dinâmica e interativa (nativa do Plotly), o que proporciona recursos visuais simples e de fácil interpretação.

## 💻 Para rodar o projeto:

* Clone o repositório:

git clone [https://github.com......)

* Crie e ative um ambiente virtual (venv):

```python -m venv venv```
```venv\Scripts\activate ```  # No Windows

* Instale as bibliotecas:

```pip install -r requirements.txt```

* Rode o Dashboard:

```streamlit run app.py```


*Vinicius - Conecte-se comigo: www.linkedin.com/in/viniciusantanam
