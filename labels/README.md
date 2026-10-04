# Generator etykiet A4

Drukuje etykiety na samoprzylepnych arkuszach A4. Jeden plik [`index.html`](index.html):
otwierasz go w przeglądarce (Chrome/Edge), nic nie trzeba instalować, działa bez internetu,
a dane nie opuszczają komputera.

## Dwa sposoby podania treści

- **Z pliku CSV**: jedna komórka to jedna etykieta. Wybierasz kolumnę; podział linii w komórce
  (Alt+Enter w Excelu) daje kolejną linię na etykiecie. Plik może mieć separator `;`, `,`
  lub tabulator i kodowanie UTF-8 albo Windows-1250 (Excel), wykrywane automatycznie.
  Przykład: [`przyklad.csv`](przyklad.csv).
- **Generator**: etykietę składasz z klocków (tekst stały, licznik, nowa linia).
  Kilka liczników może być *zagnieżdżonych* (01-01, 01-02 … 02-01) albo *równoległych*
  (01-11, 02-12 …).

## Pierwszy wydruk na nowym arkuszu / drukarce

1. Wybierz preset lub wpisz wymiary arkusza (marginesy, liczba kolumn i wierszy, odstępy).
   Rozmiar etykiety wylicza się sam.
2. Włącz **tryb kalibracji** i wydrukuj na zwykłym papierze. W oknie druku ustaw
   skalę 100%, marginesy „brak”, bez nagłówków i stopek.
3. Zmierz linijki: muszą mieć 100 mm. Przyłóż wydruk do arkusza pod światło.
4. Rozjazd całego wydruku popraw w **Korekta drukarki**, a rozjazd narastający w marginesach i odstępach.
5. Zapisz preset (**Zapisz jako…**). **Eksport** przenosi presety na inny komputer.

Opcja **Pomiń pierwsze N etykiet** pozwala dokończyć napoczęty arkusz.

## Plany

- QR / kod kreskowy z treści etykiety.
- Preset arkusza używanego w laboratorium (obecnie przykładowy Avery L7160).
