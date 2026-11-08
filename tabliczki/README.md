# Generator tabliczek na drzwi

Tabliczki przy gabinetach w układzie wzoru wydziałowego: logo UG, numer sali, wydział,
katedra lub centrum, pracownia, osoby, niebieskie paski. Całość to jeden plik
[`index.html`](index.html), który otwierasz w przeglądarce (Chrome/Edge). Nic nie trzeba
instalować, działa bez internetu, a dane nie opuszczają komputera.

## Jak używać

1. **Wczytaj dane.** Upuść CSV, np. [`przyklad.csv`](przyklad.csv) z tabliczkami z wzoru,
   albo dodaj tabliczkę przyciskiem **+ nowa**. Nowa tabliczka przejmuje nagłówek z bieżącej.
2. **Edytuj.** Wybierz tabliczkę z listy lub kliknij ją w podglądzie. Pole „Nagłówek jak w…”
   kopiuje wydział, jednostkę i pracownię z innej tabliczki.
3. **Drukuj.** Zaznaczone tabliczki drukują się, każda na osobnej stronie.
   **Eksport CSV** zapisuje aktualny stan do pliku.

Tabliczki zapisują się w przeglądarce (`localStorage`). Plik CSV to kopia do archiwum
albo przeniesienia na inny komputer.

## Zasady składu (z notatek do wzoru)

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

- Wielkie litery stawia aplikacja, więc wpisujesz normalnie.
- Osoby układają się **alfabetycznie po nazwisku**.
- Gdy tekstu jest za dużo, nagłówek albo strefa osób zmniejszają się równomiernie.
  Poniżej 70% pojawia się ostrzeżenie (czerwony procent na liście).

## CSV

Jeden wiersz to jedna osoba, a wiersze z tym samym numerem sali tworzą jedną tabliczkę.
Separator `;` (albo `,` lub tabulator), kodowanie UTF-8 albo Windows-1250.

```
sala;wydział;jednostka;pracownia;stopień;imię;nazwisko;dopisek;stanowiska
```

- Nowa linia w komórce (Alt+Enter w Excelu) dzieli jednostkę na wiersze, a w kolumnie
  `stanowiska` oddziela kolejne stanowiska.
- Kolumny wydziału, jednostki i pracowni wystarczy wypełnić w pierwszym wierszu sali.
- Import podmienia tabliczki o tych samych numerach sal, a resztę dopisuje.

## Druk

- **A4, tabliczka na środku** (domyślnie): A5 wypośrodkowana na A4, ze znacznikami cięcia
  na przedłużeniu krawędzi. Znaczniki zaczynają się 2 mm od tabliczki i kończą 5 mm przed
  brzegiem kartki.
- **Dokładnie rozmiar tabliczki**: strona 148 × 210 mm, np. do druku na papierze A5.
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

- Logo UG to PNG wycięty z wzoru w PowerPoincie (ok. 200 dpi w docelowym rozmiarze).
- Paski są przerysowane wektorowo według wzoru, więc drukują się ostro.

## Rozmiary

Geometria każdego rozmiaru to jeden wpis w stałej `FORMATS` w `index.html` (mm i pt).
A5 ma wartości odczytane z wzoru. Drugi, mniejszy rozmiar dojdzie jako kolejny wpis,
a w edytorze pojawi się wtedy wybór rozmiaru.

## Plany

- Drugi, mniejszy rozmiar tabliczki (wymiary do ustalenia).
- Logo w wersji wektorowej, gdy będzie dostępne.
