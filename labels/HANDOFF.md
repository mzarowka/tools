# HANDOFF — Generator etykiet na arkusze A4 (CSV → druk)

## Kontekst
Etykiety na próbki drukujemy zwykle na drukarce termicznej, ale ta często się zacina. Alternatywa to klasyczne samoprzylepne etykiety na arkuszu A4. Potrzebne jest proste narzędzie, które wypełnia kolejne etykiety na arkuszu danymi z pliku CSV.

## Decyzje podjęte
- **Technologia: przeglądarka (HTML + CSS + JS), jeden plik.** Wybór ze względu na agnostyczność: działa na każdym OS, nic nie trzeba instalować, a z narzędzia mogą korzystać osoby z zespołu, które nie używają R.
- **Geometria w mm, natywnie w CSS.** `@page { size: A4; margin: 0; }`, każdy arkusz to blok 210 × 297 mm, etykiety rozmieszczone w CSS grid, po każdym arkuszu wymuszony podział strony.
- **Rozmiar etykiety jest wyliczany, nie wpisywany:** (wymiar A4 − marginesy − przerwy) / liczba kolumn lub wierszy.
- **Wszystko przetwarzane lokalnie.** CSV czytany w przeglądarce (PapaParse), nic nie jest nigdzie wysyłane.
- **Bez hardkodowania.** Każdy układ arkusza to zestaw parametrów zapisywany jako preset.

## Parametry wejściowe
| Parametr | Uwagi |
|---|---|
| Marginesy: góra, dół, lewo, prawo (mm) | Osobno, bo arkusze rzadko są symetryczne |
| Liczba wierszy i kolumn | Z tego wynika rozmiar etykiety |
| Przerwy poziome i pionowe (mm) | Opcjonalne; wiele arkuszy ma odstęp między kolumnami |
| Przesunięcie globalne x/y (mm) | Korekta przesunięcia konkretnej drukarki, niezależna od marginesów |
| Offset startowy (n) | Pomija pierwsze n etykiet, żeby dało się wykorzystać napoczęty arkusz |
| Szablon treści | Kolumny CSV w szablonie, np. `{core_id}\n{depth} cm\n{date}`; nazwy kolumn brane z nagłówka CSV |
| Rozmiar czcionki + auto-shrink | Długie ID mają się mieścić w etykiecie |
| Ramki (toggle) | Tryb kalibracji: wydruk na zwykłym papierze, przyłożenie do arkusza pod światło |

## Logika
1. Każdy wiersz CSV dostaje numer slotu: `slot = offset + i`.
2. Numer slotu przeliczany jest na pozycję: `page = slot %/% (rows*cols)`, a w obrębie strony `row` i `col`. Kolejność wypełniania: od lewej do prawej, potem od góry do dołu.
3. Arkusze renderowane są jako kolejne strony. Podgląd na ekranie ma odpowiadać wydrukowi.

## UI (jedna strona)
- Strefa drop/wybór pliku CSV z podglądem wykrytych kolumn
- Panel parametrów z presetami (zapis/odczyt w `localStorage`, każdy dostęp opakowany w try/catch)
- Pole szablonu z podpowiedzią dostępnych `{kolumn}`
- Podgląd na żywo + przycisk „Drukuj”
- Widoczne przypomnienie: **skala 100% / domyślna (nie „dopasuj”), marginesy „brak”, nagłówki i stopki wyłączone**

## Znane pułapki
- Ustawień okna drukowania nie da się wymusić, więc konieczne jest wyraźne przypomnienie w UI.
- Chrome i Edge najwierniej trzymają wymiary w mm; Firefox działa poprawnie, Safari bywa kapryśne.
- „Zapisz jako PDF” z okna druku daje stały plik do archiwum lub druku z innego programu.

## Otwarte pytania
- Czy dodać QR lub kod kreskowy z kolumny ID (np. biblioteka z cdnjs)?
- Jaki jest domyślny preset, czyli jaki konkretnie arkusz etykiet mamy w laboratorium?
- Czy wystarczy podział linii w szablonie, czy potrzebne jest też formatowanie (np. pogrubiona pierwsza linia)?

## Kryteria akceptacji
- Wydruk testowy z ramkami po kalibracji pokrywa się z arkuszem z tolerancją około 0,5 mm.
- CSV z większą liczbą wierszy niż etykiet na arkuszu poprawnie dzieli się na kilka stron.
- Offset startowy działa poprawnie także przy przejściu na kolejną stronę.
- Presety są zachowywane po przeładowaniu strony.

## Preferencje autora
Kod prosty i wielokrotnego użytku, bez hardkodowania wartości. Przed pisaniem kodu najpierw omówić podejście.
