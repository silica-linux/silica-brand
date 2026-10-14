# silica-brand

Il marchio di [Silica](https://github.com/silica-linux/silica-desktop): il logo (con il nome in
Inter), le sue varianti per avvio, login e «Info su questo computer», i banner dei repository e,
più avanti, gli sfondi delle versioni. Ogni file ha la sua riga in `ASSETS.md` (autore, licenza,
fonte).

Regole clean-room come per silica-icons: nessuna forma che richiami marchi di altri sistemi.

## Il marchio

Un tetraedro SiO₄ visto dall'alto: l'unità base della silice, un atomo di silicio al centro
unito a quattro ossigeni. Il triangolo è il contorno, il centro è il silicio, i tre raggi sono i
legami; le tre facce prendono luce dall'alto a sinistra.

```
exports/
  mark/         marchio SVG: colore chiaro, colore scuro, mono (currentColor), nero, bianco;
                varianti 16, 24, 32 px con pixel-hinting
  png/          marchio PNG a 16, 32, 64, 128, 256, 512, 1024 (chiaro e scuro)
  logotype/     logotipo orizzontale e verticale: chiaro, scuro, mono, nero, bianco (testo in tracciati)
  banners/      banner GitHub 1280 × 640 per ogni repository (SVG e PNG)
  app-icon/     il marchio come icona d'app nel formato di silica-icons (livelli e anteprime)
  construction/ disegno della costruzione e dell'area di rispetto
design/
  silica-brand.sketch   pagine Costruzione, Marchio, Nome, Icona, Banner, Sistema
tools/          generatore delle esportazioni (Python)
```

Le esportazioni sono generate da `tools/build.py`, che contiene la geometria: sono loro a fare
fede. Il file Sketch le presenta e le usa (simboli del marchio, dei logotipi e del banner).

## Costruzione

Griglia di 64 unità (u) sulla tela del marchio; sulla tela 1024, 1 u = 16 px.

| Elemento | Misura |
| --- | --- |
| Triangolo mediano (asse degli spigoli) | equilatero, lato 53,20 u, apice (32; 4,75), base a y 50,82 |
| Centro | baricentro del triangolo mediano, (32; 35,46); i tre raggi lo uniscono ai vertici |
| Sagoma | il triangolo mediano allargato di 2,5 u, angoli con raggio 4 u; ingombro 56 × 49,57 u, margine laterale 4 u |
| Contorno | 5 u |
| Raggi verso il centro | 4,5 u (0,9 del contorno: tre tratti che si incontrano a 120° fanno un nodo più pesante di uno spigolo) |
| Facce | angoli con raggio 1,25 u agli acuti e 1,5 u al centro |
| Centratura ottica | il punto a metà fra il centro del riquadro della sagoma (y 28,54) e il baricentro (y 35,46) cade sul centro della tela: il riquadro sale di 3,46 u (circa h/12) |

Il marchio è fatto solo di riempimenti: la sagoma meno le tre facce dà il contorno con i tre raggi
(il monocromo); la versione a colori riempie le facce e colora il resto con il colore del bordo.

### Varianti piccole

Sotto i 48 px si usano le varianti disegnate sul pixel, ognuna alla sua misura esatta:

| Variante | Contorno (base / lati) | Raggio verticale | Raggi obliqui | Note |
| --- | --- | --- | --- | --- |
| 16 px | 1 / 1,1 px | 1 px, colonna 7 | 1 px | base sulla riga 13–14, asse a x 7,5 (0,5 px a sinistra del centro della tela, per tenere nitido il raggio verticale) |
| 24 px | 2 / 2,1 px | 2 px, colonne 11–12 | 1,8 px | base sulle righe 18–20 |
| 32 px | 2 / 2,5 px | 2 px, colonne 15–16 | 2,2 px | base sulle righe 25–27 |

Le linee orizzontali e verticali cadono su pixel interi; i lati obliqui sono un po' più spessi della
base perché l'antialiasing li alleggerisce. In queste varianti il triangolo è equilatero entro
mezzo pixel.

## Uso

- **Marchio da solo**: icona del sistema, avvio, favicon, avatar dei repository.
- **Logotipo orizzontale**: intestazioni, sito, banner, schermata di login.
- **Logotipo verticale**: schermata di avvio, «Info su questo computer», copertine.
- **Colore su chiaro** (`*-light`) su fondi chiari, **colore su scuro** (`*-dark`) su fondi scuri;
  il bordo si fonde con il fondo e le facce restano separate.
- **Monocromo** quando il colore non c'è o non si legge: nero su chiaro, bianco su scuro o su
  foto; `*-mono.svg` usa `currentColor`.

Logotipo, con H = altezza della sagoma del marchio: nome in Inter SemiBold (600), spaziatura
−0,02 em. Orizzontale: maiuscola alta 0,5 H, luce fra marchio e nome 0,3 H, linea di base sulla
base del marchio. Verticale: maiuscola alta 0,382 H (H / φ²), luce 0,3 H, nome centrato.

## Colori

| Nome | Hex | Uso |
| --- | --- | --- |
| Silice chiaro | `#A9CCFF` | faccia sinistra |
| Silice | `#5B9BFF` | faccia destra |
| Silice profondo | `#2F6FE4` | faccia inferiore |
| Inchiostro | `#16181C` | testo su chiaro, fondo scuro; bordo su scuro al 55 % |
| Carta | `#F5F6F8` | testo su scuro, fondo chiaro |
| Bordo su chiaro | `#FFFFFF` al 92 % | contorno e raggi della versione chiara |

## Area di rispetto

Intorno al marchio e ai logotipi resta libero un margine di **H/4** su ogni lato (H = altezza
della sagoma). Dentro l'area non vanno testo, bordi o altri segni.

## Dimensione minima

- Marchio: **16 px** (con la variante 16); in stampa 5 mm di altezza.
- Logotipo: marchio alto almeno **24 px** (logotipo orizzontale largo 72 px); in stampa 20 mm di
  larghezza.

## Cosa non fare

- Non deformare, ruotare, inclinare o specchiare il marchio.
- Non cambiare i colori delle facce né il loro ordine (la luce viene dall'alto a sinistra).
- Non aggiungere ombre, contorni, riflessi o effetti di vetro al marchio: il vetro è
  dell'interfaccia, non del logo.
- Non ridisegnare il nome con un altro font, peso o spaziatura; non scrivere «SILICA» in maiuscolo
  nel logotipo.
- Non cambiare le proporzioni fra marchio e nome né la luce fra i due.
- Non usare le varianti 16, 24 e 32 a misure diverse dalla loro, e non scendere sotto la
  dimensione minima.
- Non mettere il marchio a colori su fondi a medio contrasto o su foto: lì va il monocromo.
- Non accostarlo a marchi di altri sistemi o usarlo per prodotti che non sono Silica.

## Rigenerare le esportazioni

Serve Inter variabile (OFL, [rsms/inter](https://github.com/rsms/inter), v4) fuori dal
repository:

```
python3 -m venv venv && venv/bin/pip install -r tools/requirements.txt
venv/bin/python tools/build.py --inter <percorso>/Inter-VariableFont_opsz,wght.ttf
```

## Licenza

**Da decidere.** Un marchio di solito non è riusabile liberamente: finché la licenza non è
scelta, i file di questo repository non si usano fuori dal progetto Silica. Per il codice in `tools/`
si propone MIT OR Apache-2.0, come negli altri repository. Inter è OFL 1.1 e nei file c'è solo come
tracciati.
