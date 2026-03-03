import pytest
from zadanie1 import Produkt, Klient, Promocja, oblicz_koszyk, waliduj_wejscie

# test 1 pusty koszyk
def test_pusty_koszyk():
    klient = Klient("K1", "standard")
    with pytest.raises(ValueError):
        oblicz_koszyk([], klient, [])

# test 2 brak klienta
def test_brak_klienta():
    p = Produkt("SKU1", "Produkt", "books", 50, 0.23, 1)
    with pytest.raises(ValueError):
        oblicz_koszyk([p], None, [])

# test 3 zla cena
def test_zla_cena():
    p = Produkt("SKU1", "Produkt", "books", -10, 0.23, 1)
    klient = Klient("K1", "standard")
    with pytest.raises(ValueError):
        oblicz_koszyk([p], klient, [])

# test 4 rabat procentowy
def test_rabat_procentowy():
    p = Produkt("SKU1", "Ksiazka", "books", 100, 0.05, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("procent", 15, kategoria="books")
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] == 85.0

# test 5 outlet nie dostaje rabatu procentowego
def test_outlet_bez_rabatu():
    p = Produkt("OUT1", "Outlet rzecz", "outlet", 100, 0.23, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("procent", 15, kategoria="outlet")
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] == 100.0

# test 6  2+1 
def test_2plus1_qty3():
    p = Produkt("SKU1", "Koszulka", "clothes", 90, 0.23, 3)
    klient = Klient("K1", "standard")
    promo = Promocja("2plus1", 0, sku_lista=["SKU1"])
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] == 60.0

# test 7  2+1 
def test_2plus1_qty2():
    p = Produkt("SKU1", "Koszulka", "clothes", 90, 0.23, 2)
    klient = Klient("K1", "standard")
    promo = Promocja("2plus1", 0, sku_lista=["SKU1"])
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] == 90.0

# test 8  2+1 
def test_2plus1_qty4():
    p = Produkt("SKU1", "Koszulka", "clothes", 60, 0.23, 4)
    klient = Klient("K1", "standard")
    promo = Promocja("2plus1", 0, sku_lista=["SKU1"])
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] == 45.0

# test 9  darmowa dostawa powyzej progu
def test_darmowa_dostawa():
    p = Produkt("SKU1", "Drogi produkt", "electronics", 250, 0.23, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("darmowa_dostawa", 0, prog=200)
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["koszt_dostawy"] == 0

# test 10  platna dostawa ponizej progu
def test_platna_dostawa():
    p = Produkt("SKU1", "Tani produkt", "electronics", 50, 0.23, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("darmowa_dostawa", 0, prog=200)
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["koszt_dostawy"] == 15.0

# test 11  kupon nie laczy sie z 2+1
def test_kupon_nie_laczy_z_2plus1():
    p = Produkt("SKU1", "Koszulka", "clothes", 90, 0.23, 3)
    klient = Klient("K1", "standard")
    promo1 = Promocja("2plus1", 0, sku_lista=["SKU1"])
    promo2 = Promocja("kupon", 20, prog=50)
    paragon = oblicz_koszyk([p], klient, [promo1, promo2])
    assert paragon["linie"][0]["cena_po"] == 60.0

# test 12 cena nie spada ponizej 1 zl
def test_cena_min_1zl():
    p = Produkt("SKU1", "Tani produkt", "books", 2, 0.05, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("procent", 90, kategoria="books")
    paragon = oblicz_koszyk([p], klient, [promo])
    assert paragon["linie"][0]["cena_po"] >= 1.0

# test 13 najtanszy 50% w kategorii
def test_najtanszy_50():
    p1 = Produkt("SKU1", "Droga koszulka", "clothes", 200, 0.23, 1)
    p2 = Produkt("SKU2", "Tania koszulka", "clothes", 50, 0.23, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("najtanszy_50", 50, kategoria="clothes")
    paragon = oblicz_koszyk([p1, p2], klient, [promo])
    assert paragon["linie"][1]["cena_po"] == 25.0
    assert paragon["linie"][0]["cena_po"] == 200.0

# test 14  nieznany typ promocji
def test_nieznany_typ_promocji():
    p = Produkt("SKU1", "Produkt", "books", 50, 0.23, 1)
    klient = Klient("K1", "standard")
    promo = Promocja("mega_rabat", 50)
    with pytest.raises(ValueError):
        oblicz_koszyk([p], klient, [promo])

# test 15  paragon zawiera poprawne podsumowanie
def test_paragon_podsumowanie():
    p = Produkt("SKU1", "Produkt", "electronics", 100, 0.23, 2)
    klient = Klient("K1", "gold")
    paragon = oblicz_koszyk([p], klient, [])
    assert paragon["suma_brutto"] == 200.0
    assert paragon["do_zaplaty"] == 215.0 
    assert paragon["klient_id"] == "K1"
