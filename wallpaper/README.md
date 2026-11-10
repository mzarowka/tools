# Generator tapet katedry

Tapeta pulpitu z logo i nazwą katedry oraz dopiskiem, który może być inny na każdym
komputerze (np. gdzie zapisywać pliki). Jeden plik [`index.html`](index.html):
otwierasz go w przeglądarce, nic nie trzeba instalować, działa bez internetu.

## Użycie

1. Wpisz dopisek. Każda linia to osobny wiersz; linia w `**gwiazdkach**` jest pogrubiona.
   Puste pole daje tapetę z samym logo.
2. Ustaw rozdzielczość: wybierz z listy albo kliknij **Ten ekran** na komputerze docelowym.
   Wynik uwzględnia skalowanie systemu (np. 125% w Windows).
3. Wybierz wariant ciemny lub jasny.
4. **Pobierz PNG** i ustaw obraz jako tapetę.

## Poziomice

Tło to poziomice wygenerowane z **ziarna**: ten sam tekst ziarna daje zawsze tę samą rzeźbę,
w każdej rozdzielczości. Można więc nadać każdemu komputerowi własne ziarno (np. jego nazwę).
Co piąta poziomica jest grubsza, jak poziomica główna na mapie. Suwaki regulują gęstość,
skalę rzeźby, widoczność i wyciszenie poziomic pod napisami.

## Odtwarzanie tapety

Wszystkie ustawienia są zapisane w adresie strony (pole **Link do tej tapety**). Zachowaj
link, a tapetę danego komputera da się odtworzyć albo poprawić później.

## Pliki

- `index.html`: generator. Logo i font są wbudowane na końcu pliku.
- `logo.svg`: logo katedry w wersji wektorowej, przerysowane automatycznie (potrace) z PNG.
  Przydaje się też poza generatorem.

Font: [DM Sans](https://github.com/googlefonts/dm-fonts) (400/600/700), licencja SIL Open Font License 1.1.

Stałe treści (nazwa katedry, domyślny dopisek, proporcje układu, presety rozdzielczości,
kolory wariantów) są w obiekcie `CONFIG` na początku skryptu.
