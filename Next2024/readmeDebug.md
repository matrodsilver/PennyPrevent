# Notas

Linha 23:
 - Lógica impede que ´dados´ seja ´None´, mas Pylancer indica erro esperando essa possibilidade, por isso a condicional foi adicionada

Linha 63 | 127:
- Mudar condição do else para método mais industrial                                  !

Linhas 116:
- Colocar resto do chatbot dentro da função do chatbot                                !

Linha 119:
- Tentar colocar teste manual em página separada                                      !

Linha 138:
- trivia: Se 2 valores do dicionário são iguais, mostra o primeiro

Linha 141:
- Tentar colocar download do modelo em página separada                                !

Linha 148:
- No momento, chatbot só é ativo após o teste manual

Linhas 251:
- O mesmo que linha 23, mas comparando ´dados´ com um ´dataFrame´ pandas

Linhas 315 | 357:
- Colocar condicional: 'Se o último dado tem index diferente'                          !

Linha 323:
- Streamlit entra em conflito tentando rodar pushbullet (separar scripts)

Linhas 354:
- Tentar colocar texto de predição em tempo real em outra página, e uma de cada vez    !

Linhas 340:
- copilot:

  "The ´\´ character in Python is a line continuation character. It allows you to split a single logical line of code across multiple physical lines for better readability"


  obs:
-  Várias linhas estão com lógica implementada de modo que o Pylancer não sinalize avisos de erro. Apesar dessas linhas poderem ser retiradas e o código rodar normalmente sem elas, elas evitam error squiggles no código.

- É possível colocar '''[algum texto ou html]''' entre essas três aspas para usar html em multiplas linhas no sl.markdown()
  exemplo: linha 292

- Não testei o chat bot para não gastar crédito, creio q é só mudar ´chatbot´ pra ´True´
