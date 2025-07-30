# BlipNlpTest

Essa é uma classe que permite o teste de mensagens em provedores integrados na plataforma, com o retorno do conteúdo cadastrado no Assistente de Conteudo.

## Instalação

Para instalar o pacote, basta executar o comando abaixo:

<pre><code>pip install blipnlptest</code></pre>

## Uso

Após a instalação do pacote, você terá acesso a classe que permitirá a execução do teste.

Os parâmetros necessários são:

- data (opcional) : Dataframe de entrada
- resource (opcional) : Nome do recurso com o texto de tests
- threshold (opcional) : float referente ao threshold do provedor com valores entre 0.1 (10%) a 1.0 (100%). (default: 0.5)
- key: chave do bot
- contract_id: id do contrato.

Exemplo do código:


Caso a análise seja de dados já analisados pelo provedor (envie um dataframe que tenha no mínimo as colunas Text, Intentions, Entities e Score), use:

<pre><code>

import blipnlptest as bnt

cc = bnt.contentchecker(key, data=df, contract_id="cliente_x")
cc.identityanalysis()
</code></pre>

Se a análise for feita com dados que não foram analisados (envie um dataframe que a coluna de texto tenha o nome Text), use:

<pre><code>
import blipnlptest as bnt

cc = bnt.contentchecker(key, data=df)
cc.sentences()
</code></pre>

OBS: A divisão foi feita para que os dados já rotulados não realizem outra análise no provedor.

Caso queira analisar com dados que não estejam na base de dados, utilize o recurso do bot. O recurso deverá ser do tipo texto, e as mensagens separadas por vírgula. Use:

<pre><code>

import blipnlptest as bnt

cc = bnt.contentchecker(key, resource='nome_do_recurso')
cc.byresource()
</code></pre>

Em todos os casos, você pode colocar o valor do threshold personalizado, da seguinte forma:

<pre><code>
cc = bnt.contentchecker(key, data=df,threshold=0.6)
cc.sentences()
</code></pre>

Com os parâmetros previamente atribuídos, rodando o código acima você terá como saída a exibição do resultado com:

- A mensagem de entrada;
- A intenção reconhecida;
- As entidades reconhecidas;
- O score;
- A resposta entregue pelo Assistente de Conteudo;
- Se foi entregue (y/n);
- Ponto de atenção.

Os pontos de atenção são sugestões de pontos para observar, eles tem os status abaixo:

- model = Se o score for baixo e não retornar conteúdo, necessário avaliar o aumento da confiança no modelo;
- refine = Se o score for baixo e existir uma resposta no Assistente de Conteudo, é necessário refinar e entender os próximos passos (aumentar a confiança ou ajustar os exemplos de alguma intenção);
- valid = Se o score for alto e retornou uma resposta, avaliar se a resposta está válida.
- content | entity in the combination = Se o score estiver alto, foi identificada entidade e não retornou uma resposta, é válido checar a falta da entidade na combinação;
- content | entity in the model = Se o score estiver alto, e não foi identificada alguma entidade, é válido checar a falta dela no modelo (que se criada, consequentemente irá impactar o conteúdo.

## Licença

Esse projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
