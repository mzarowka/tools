# Generator tabliczek na drzwi

Tabliczki przy pomieszczeniach w układzie wzoru wydziałowego. Są trzy rodzaje:

- **A5 gabinet (148 × 210 mm, pionowo)**: logo UG, numer sali, wydział, katedra lub
  centrum, pracownia, osoby, niebieskie paski.
- **A5 pomieszczenie (148 × 210 mm, pionowo)** dla laboratoriów w pełnym rozmiarze: ta sama
  rama co gabinet, ale zamiast osób jest duża **nazwa pomieszczenia**, a nagłówek nie ma
  pracowni.
- **Mała (146 × 100 mm, poziomo)** przy laboratoriach i składach: logo UG, numer sali,
  wydział, katedra i duża nazwa pomieszczenia.

Pomieszczenia (laboratoria, składy) należą do katedry, dlatego ich tabliczki nie mają
osób ani pracowni.

Całość to jeden plik [`index.html`](index.html), który otwierasz w przeglądarce
(Chrome/Edge). Nic nie trzeba instalować, działa bez internetu, a dane nie opuszczają
komputera.

## Jak używać

1. **Wczytaj dane.** Upuść CSV, np. [`przyklad.csv`](przyklad.csv), albo dodaj tabliczkę
   przyciskiem **+ nowa**. Nowa tabliczka przejmuje rozmiar i nagłówek z bieżącej.
2. **Edytuj.** Wybierz tabliczkę z listy lub kliknij ją w podglądzie. Pole **Rozmiar**
   przełącza rodzaj tabliczki, a edytor pokazuje tylko pola używane przez dany rozmiar.
   „Nagłówek jak w…” kopiuje wydział i jednostkę z innej tabliczki.
3. **Drukuj.** Zaznaczone tabliczki drukują się po kolei, każdy rozmiar na osobnych
   kartkach. **Eksport CSV** zapisuje aktualny stan do pliku.

Tabliczki zapisują się w przeglądarce (`localStorage`). Plik CSV to kopia do archiwum
albo przeniesienia na inny komputer.

## Zasady składu

A5 gabinet, według notatek do wzoru w PowerPoincie:

| Element | Styl |
|---|---|
| Numer sali | 44 pt, pogrubiony, niebieski UG |
| Wydział | 14 pt, wielkie litery |
| Katedra / centrum | 24 pt, pogrubiona, wielkie litery; Enter = nowa linia |
| Pracownia | 14 pt, wielkie litery (opcjonalnie) |
| Osoba (stopień imię nazwisko) | 20 pt, pogrubiona |
| Dopisek, np. „prof. Uniwersytetu Gdańskiego” | 16 pt, pisownia jak wpisana |
| Stanowiska | 16 pt, wielkie litery, każde w osobnej linii |
| Odstęp między osobami | 2 puste wiersze nazwiska |

A5 pomieszczenie: numer, wydział i katedra jak na gabinecie, a w miejscu osób
nazwa pomieszczenia: 36 pt, pogrubiona, wielkie litery, czarna; do 3 linii.

Mała tabliczka:

| Element | Styl |
|---|---|
| Numer sali | 30 pt, pogrubiony, niebieski UG |
| Wydział | 10 pt, wielkie litery |
| Katedra / centrum | 13 pt, pogrubiona, wielkie litery; Enter = nowa linia |
| Nazwa pomieszczenia | 30 pt, pogrubiona, wielkie litery, czarna; do 2 linii |

- Wielkie litery stawia aplikacja, więc wpisujesz normalnie.
- Osoby układają się **alfabetycznie po nazwisku**.
- Słowa łamią się tylko na spacjach (albo tam, gdzie wstawisz Enter). Za długie słowo
  albo nazwa, która nie mieści się w limicie linii, zmniejsza się w całości.
- Gdy tekstu jest za dużo, dana strefa (nagłówek, osoby, nazwa) zmniejsza się równomiernie.
  Poniżej 70% pojawia się ostrzeżenie (czerwony procent na liście).

## CSV

Jeden wiersz to jedna osoba, a wiersze z tym samym numerem sali tworzą jedną tabliczkę.
Separator `;` (albo `,` lub tabulator), kodowanie UTF-8 albo Windows-1250.

```
sala;rozmiar;pomieszczenie;wydział;jednostka;pracownia;stopień;imię;nazwisko;dopisek;stanowiska
```

- `rozmiar`: `a5` (gabinet), `a5-pomieszczenie` albo `mała`. Pusta wartość lub brak kolumny oznacza A5, więc starsze
  pliki dalej działają.
- `pomieszczenie`: nazwa pomieszczenia na tabliczce pomieszczenia (A5 lub małej). Kolumny osób zostają wtedy puste.
- Nowa linia w komórce (Alt+Enter w Excelu) dzieli tekst na wiersze, a w kolumnie
  `stanowiska` oddziela kolejne stanowiska.
- Kolumny nagłówka (rozmiar, pomieszczenie, wydział, jednostka, pracownia) wystarczy
  wypełnić w pierwszym wierszu sali.
- Import podmienia tabliczki o tych samych numerach sal, a resztę dopisuje.

Trzy ostatnie sale w `przyklad.csv` (B301, B317, B302) to zmyślone przykłady tabliczek pomieszczeń.
Pozostałe pochodzą z wzoru.

## Druk

- **A4** (domyślnie): na kartce mieści się tyle tabliczek, ile wynika z wymiarów. Wychodzi
  jedna A5 albo dwie małe, jedna nad drugą, całość wyśrodkowana. Znaczniki cięcia biegną
  na przedłużeniu krawędzi: od 2 mm za tabliczką do brzegu kartki (z zapasem 5 mm) albo
  do sąsiedniej tabliczki.
- **Dokładnie rozmiar tabliczki**: każda tabliczka na stronie swojego rozmiaru
  (148 × 210 lub 146 × 100 mm).
- **Obrys**: cienka ramka po krawędzi, jak we wzorze z PowerPointa.

W oknie drukowania ustaw skalę 100% (nie „dopasuj”), marginesy „brak”, wyłącz nagłówki
i stopki, a grafikę tła włącz.

## Czcionka Aptos

Wzór jest złożony krojem Aptos, czyli domyślną czcionką nowego Office. Aptos nie jest
dołączony do repozytorium, bo to czcionka Microsoftu i jej licencja nie pozwala jej
rozpowszechniać. Aplikacja szuka go w tej kolejności:

1. plik wczytany w sekcji **Czcionka Aptos** (`Aptos.ttf` i `Aptos-Bold.ttf`), zapamiętany
   w tej przeglądarce (IndexedDB);
2. Aptos zainstalowany w systemie;
3. czcionka zastępcza (Segoe UI / Arial). Wtedy tabliczka wygląda inaczej niż wzór.

Status w panelu pokazuje, która wersja jest w użyciu. Jeśli Aptosa nie ma w systemie,
a jest w Office, bywa pobierany „z chmury” i przeglądarka go nie widzi. Wtedy wystarczy
raz wczytać pliki.

## Grafika

- Logo UG jest wektorowe, z oficjalnego pliku `UG_logo_CMYK_podstawowy_pozytyw_PL.pdf`
  (przycięte do kształtów, wbudowane w `index.html`). Ma jeden pełny kolor, niebieski UG,
  bez odcieni pośrednich. Wcześniejsze logo z PNG dawało na wydruku żółtą obwódkę, bo
  drukarka składała jasne odcienie na krawędziach z kilku tuszy.
- Paski są przerysowane wektorowo według wzoru, więc drukują się ostro.

## Rozmiary

Geometria każdego rozmiaru to jeden wpis w stałej `FORMATS` w `index.html` (mm i pt).
Wpis wymienia też elementy, które tabliczka ma (logo, numer, nagłówek, osoby, nazwa
pomieszczenia, paski). Kolejny rozmiar to kolejny wpis, bez zmian w reszcie kodu.

- A5 ma wartości odczytane z wzoru. Oba warianty A5 korzystają ze wspólnej ramy
  (`A5_FRAME`), więc poprawka logo, numeru, nagłówka albo pasków obejmuje oba.
- Mała ma wymiar zmierzony na starej kartce (146 × 100 mm) i układ zaprojektowany na
  wzór A5. Po pierwszym wydruku warto przyłożyć kartkę do ramki.

## Plany

- Potwierdzić wymiar małej tabliczki wydrukiem próbnym w ramce.
