# Roteiro do pitch

**Duração alvo: 3 minutos e 30 segundos.** Mostre o README, o terminal e os arquivos de saída enquanto apresenta.

## 0:00 a 0:35 | O problema

“A Sabor Express precisa coordenar entregas simultâneas durante o pico. Quando dois entregadores cruzam as mesmas regiões em ordens pouco eficientes, o tempo e a distância aumentam. Minha proposta monta duas rotas que saem do restaurante, atendem todos os pedidos e voltam ao ponto de partida.”

## 0:35 a 1:15 | O mapa e o A*

[Mostrar o grafo no README e apontar a rua de mão única.]

“Modelei o mapa como um grafo direcionado. Os cruzamentos são nós e as ruas são ligações com tempo e distância. Existem pesos para tráfego normal e de pico. Para ligar duas paradas, o A* soma o tempo já percorrido a uma estimativa mínima baseada na distância em quadras. Ele respeita o sentido das ruas. Comparei seus resultados com Dijkstra e os custos mínimos coincidiram em todos os pares testados.”

## 1:15 a 2:05 | Agrupamento e ordem

[Mostrar as funções kmeans e optimize em src/rotas.py.]

“O K-Means separa os pedidos em duas zonas com base nas coordenadas. Para cada grupo pequeno, o código testa as ordens possíveis e escolhe a de menor tempo, incluindo o retorno. Para grupos maiores que sete pedidos, o programa usa o vizinho mais próximo para evitar testar todas as ordens. O custo entre paradas vem do A*.”

## 2:05 a 3:00 | Demonstração e resultado

[Executar `python src/rotas.py` e abrir outputs/rotas.csv.]

“Comparei três planos usando os mesmos pedidos. No pico, o plano que segue a ordem de chegada soma 120 minutos. Otimizar a ordem nos mesmos grupos reduz o total para 80. Agrupar por região e otimizar a ordem reduz para 54 minutos. É uma queda de 55% em relação à referência simulada. A distância total cai de 12,8 para 6,4 quilômetros. Aqui no CSV é possível conferir a ordem das paradas e as ruas percorridas por cada entregador.”

## 3:00 a 3:30 | Limitações

“Os dados são simulados. O experimento mede deslocamento, sem contar tempo para entregar o pedido ao cliente. Uma validação com a Sabor Express precisaria usar pedidos e tempos reais para medir pontualidade e verificar como as rotas se comportam durante o dia.”

Após gravar, publique o vídeo no YouTube como não listado e envie o link junto com o do repositório público.

