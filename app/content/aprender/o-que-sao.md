---
titulo: O que são estereogramas
ordem: 1
resumo: Imagens 2D que escondem cenas tridimensionais, visíveis a olho nu quando você descansa o foco — e por que isso funciona.
fontes:
  - 'Julesz, B. (1971). <em>Foundations of Cyclopean Perception</em>. University of Chicago Press.'
  - 'Tyler, C. W., & Clarke, M. B. (1990). The Autostereogram. <em>SPIE Stereoscopic Displays and Applications</em>, 1256.'
  - 'Wikipedia — <a href="https://en.wikipedia.org/wiki/Autostereogram" rel="noopener">Autostereogram</a>'
  - 'Scholarpedia — <a href="http://www.scholarpedia.org/article/Autostereogram" rel="noopener">Autostereogram</a>'
---

Um estereograma é uma imagem chata — bidimensional, impressa numa folha ou
exibida numa tela — que **esconde uma cena tridimensional**. Quando você
olha do jeito certo, uma forma emerge: um golfinho saltando, um coração
flutuando, letras suspensas no ar. A imagem não muda. Quem muda é o seu
olhar.

Esse efeito, que parece mágico, é geometria pura. O cérebro processa dois
pontos de vista ligeiramente diferentes (um por olho) e reconstrói
profundidade a partir das diferenças entre eles — a chamada **disparidade
binocular**. Estereogramas exploram esse mecanismo: a imagem 2D é
desenhada de tal forma que, quando os dois olhos focam pontos
*deslocados* da figura, o cérebro interpreta esse deslocamento como
distância.

## Não é uma família, são várias

A palavra "estereograma" cobre técnicas bem diferentes. As três
principais:

**Pares estéreo** (1838, Charles Wheatstone). Duas fotografias quase
idênticas, tiradas de pontos de vista separados pela mesma distância dos
olhos humanos. Você olha cada uma com um olho, geralmente usando um
visualizador (como os antigos *View-Master* da Mattel), e o cérebro
funde. Foi a primeira evidência de que a profundidade vem da disparidade,
não só de pistas visuais como sombra e perspectiva.

**Random Dot Stereograms** (1960, Béla Julesz nos Bell Labs). Um par
estéreo onde cada imagem, sozinha, parece ruído branco — pixels
aleatórios sem forma. Quando funde os dois com o cérebro, uma forma 3D
aparece. Julesz inventou isso para provar que a percepção de profundidade
é **puramente estatística**: o cérebro consegue casar pontos entre as
duas imagens mesmo sem nenhuma pista monocular (contorno, sombra,
textura). Os random dot stereograms foram o primeiro grande achado da
psicofísica visual moderna.

**Single Image Random Dot Stereograms — SIRDS** (1979, Christopher Tyler).
A grande revolução: e se a *mesma* imagem servisse pros dois olhos? Tyler
percebeu que dá pra desenhar um único padrão repetido horizontalmente,
onde a **largura da repetição varia conforme a profundidade**. Os dois
olhos, ao focar em pontos diferentes da repetição, "casam" como se
estivessem olhando um par estéreo — sem precisar de óculos, sem precisar
de visualizador. Foi essa descoberta que virou a moda Magic Eye dos anos
1990.

> O termo *autoestereograma* é mais preciso pra essa terceira família — é
> a imagem que se sustenta sozinha, sem par. Mas "estereograma", na fala
> comum, virou sinônimo do estilo Magic Eye. É esse o foco do site.

## Anatomia de um SIRDS

Olhe pra um Magic Eye qualquer. Você vê:

- **Um padrão repetido horizontalmente.** Pode ser ruído colorido,
  pequenas figuras, ou textura abstrata. O que importa é que ele se
  repete numa distância aproximada.
- **Uma variação sutil dessa repetição.** Em algumas regiões, a distância
  entre repetições é levemente menor. Em outras, levemente maior.

A variação é o que codifica a profundidade. Pontos mais "próximos" do
observador (no objeto escondido) têm repetição mais comprimida; pontos
mais "distantes" têm repetição mais larga. Quando seus olhos relaxam o
foco e cada um "trava" em uma cópia diferente do padrão, o cérebro lê a
diferença entre as cópias como distância — exatamente como faria diante
de uma cena 3D real.

A matemática por trás dessa variação é o assunto da parte
[O cálculo](/aprender/calculo). Por enquanto, basta sentir que existe um
truque geométrico — não é IA, não é magia, é um cálculo que se faz no
papel.

## Como ver o 3D

Há duas técnicas básicas. Funcionam pela mesma física, com profundidade
percebida invertida.

**Paralela (wall-eyed).** Os olhos se "relaxam" como se estivessem
olhando ao longe. Boa para imagens onde a figura deve **saltar pra fora**
do papel. É a técnica usada nos livros Magic Eye originais.

**Cruzada (cross-eyed).** Os olhos cruzam levemente, como se você
focasse num objeto bem na frente do nariz. A imagem é vista invertida:
o que sairia, agora **afunda**.

A dica clássica: aproxime o nariz da imagem, foque "através" dela, e
afaste devagar mantendo o relaxamento. O cérebro leva alguns segundos
pra travar — e quando trava, a forma surge inteira de uma vez. Não vem
em fade-in. É discreto: vê ou não vê.

Pessoas com forte dominância de um olho, ou com diferença grande de
acuidade entre os dois (anisometropia), podem ter dificuldade
permanente. Estereogramas só funcionam pra quem tem **visão binocular
funcional** — outra evidência indireta de que o efeito depende da
geometria de dois pontos de vista, não de truque psicológico.

## Onde aparecem

Estereogramas saíram do laboratório em duas ondas. A primeira foi
educacional — durante os anos 1970 e 80, viraram ferramenta padrão em
pesquisas de neurociência da visão, justamente pelo motivo que Julesz
descobriu: isolam a disparidade binocular de qualquer outra pista. Se
você quer estudar profundidade pura, SIRDS é o jeito.

A segunda foi cultural. Em 1991, a empresa N.E. Thing Enterprises (depois
rebatizada Magic Eye Inc.) publicou os primeiros livros comerciais. Em
poucos anos, posters de Magic Eye estavam em shoppings, capas de revista,
camisetas. O auge foi 1994–95, durou pouco — mas marcou geração.

Hoje, estereogramas vivem em três lugares: ciência da visão (ainda
relevante), arte digital de nicho, e — graças a algoritmos como o que
esse site implementa — em qualquer computador, gerados em tempo real a
partir de um mapa de profundidade.

A história inteira — de Wheatstone em 1838 ao Magic Eye no shopping —
está no próximo artigo.
