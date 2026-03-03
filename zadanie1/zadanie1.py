import math

produkty_w_sklepie = ["electronics", "books", "clothes", "outlet", "sport", "food"]

class Produkt:
    def __init__(self, sku, nazwa, kategoria, cena_brutto, vat, ilosc):
        self.sku = sku
        self.nazwa = nazwa
        self.kategoria = kategoria
        self.cena_brutto = cena_brutto
        self.vat = vat
        self.ilosc = ilosc
        self.rabat = 0
        self.cena_po_rabacie = cena_brutto

class Klient:
    def __init__(self, id, loyalty):
        self.id = id
        self.loyalty = loyalty

class Promocja:
    def __init__(self, typ, wartosc, kategoria=None, sku_lista=None, prog=None, kupon_kod=None):
        self.typ = typ
        self.wartosc = wartosc
        self.kategoria = kategoria
        self.sku_lista = sku_lista
        self.prog = prog
        self.kupon_kod = kupon_kod
        self.aktywna = True

def waliduj_wejscie(produkty, klient, promocje):
    if produkty == None or len(produkty) == 0:
        raise ValueError("Koszyk jest pusty")
    if klient == None:
        raise ValueError("Brak danych klienta")
    for p in produkty:
        if p.cena_brutto <= 0:
            raise ValueError("Cena musi byc wieksza od 0")
        if p.ilosc <= 0:
            raise ValueError("Ilosc musi byc wieksza od 0")
        if p.vat < 0 or p.vat > 1:
            raise ValueError("VAT musi byc miedzy 0 a 1")
        if p.sku == None or p.sku == "":
            raise ValueError("SKU nie moze byc puste")
        if p.nazwa == None or p.nazwa == "":
            raise ValueError("Nazwa nie moze byc pusta")
    for promo in promocje:
        if promo.typ not in ["procent", "kupon", "2plus1", "darmowa_dostawa", "najtanszy_50"]:
            raise ValueError("Nieznana promocja: " + promo.typ)
    return True

def zastosuj_procent(produkty, promo):
    for p in produkty:
        if p.kategoria == promo.kategoria and p.kategoria != "outlet":
            rabat = p.cena_brutto * promo.wartosc / 100
            p.rabat = p.rabat + rabat
            p.cena_po_rabacie = p.cena_brutto - p.rabat
            if p.cena_po_rabacie < 1:
                p.rabat = p.cena_brutto - 1
                p.cena_po_rabacie = 1
    return produkty

def zastosuj_kupon(produkty, promo, uzyto_2plus1):
    if uzyto_2plus1 == True:
        return produkty
    suma = 0
    for p in produkty:
        suma = suma + p.cena_po_rabacie * p.ilosc
    if promo.prog != None and suma < promo.prog:
        return produkty
    if suma <= 0:
        return produkty
    do_rozdzielenia = promo.wartosc
    if do_rozdzielenia > suma - len(produkty) * 1:
        do_rozdzielenia = suma - len(produkty) * 1
    if do_rozdzielenia <= 0:
        return produkty
    for p in produkty:
        udzial = (p.cena_po_rabacie * p.ilosc) / suma
        rabat_dla_produktu = do_rozdzielenia * udzial / p.ilosc
        p.rabat = p.rabat + rabat_dla_produktu
        p.cena_po_rabacie = p.cena_brutto - p.rabat
        if p.cena_po_rabacie < 1:
            p.rabat = p.cena_brutto - 1
            p.cena_po_rabacie = 1
    return produkty

def zastosuj_2plus1(produkty, promo):
    wynik = False
    for p in produkty:
        if promo.sku_lista != None and p.sku in promo.sku_lista:
            if p.ilosc >= 3:
                ile_darmowych = p.ilosc // 3
                rabat = ile_darmowych * p.cena_po_rabacie
                p.rabat = p.rabat + rabat / p.ilosc
                p.cena_po_rabacie = p.cena_brutto - p.rabat
                if p.cena_po_rabacie < 1:
                    p.rabat = p.cena_brutto - 1
                    p.cena_po_rabacie = 1
                wynik = True
            elif p.ilosc == 2:
                pass  
    return produkty, wynik

def zastosuj_najtanszy_50(produkty, promo):
    najtanszy = None
    najtansza_cena = float('inf')
    for p in produkty:
        if promo.kategoria != None and p.kategoria != promo.kategoria:
            continue
        if p.cena_po_rabacie < najtansza_cena:
            najtansza_cena = p.cena_po_rabacie
            najtanszy = p
    if najtanszy != None:
        rabat = najtanszy.cena_po_rabacie * 0.5
        najtanszy.rabat = najtanszy.rabat + rabat
        najtanszy.cena_po_rabacie = najtanszy.cena_brutto - najtanszy.rabat
        if najtanszy.cena_po_rabacie < 1:
            najtanszy.rabat = najtanszy.cena_brutto - 1
            najtanszy.cena_po_rabacie = 1
    return produkty

def oblicz_dostawe(produkty, promo):
    suma = 0
    for p in produkty:
        suma = suma + p.cena_po_rabacie * p.ilosc
    if promo.prog != None and suma >= promo.prog:
        return 0
    else:
        return 15.0 

def generuj_paragon(produkty, klient, koszt_dostawy):
    paragon = {}
    paragon["linie"] = []
    suma_brutto = 0
    suma_rabat = 0
    suma_netto = 0
    suma_vat = 0
    for p in produkty:
        linia = {}
        linia["sku"] = p.sku
        linia["nazwa"] = p.nazwa
        linia["ilosc"] = p.ilosc
        linia["cena_przed"] = round(p.cena_brutto, 2)
        linia["cena_po"] = round(p.cena_po_rabacie, 2)
        linia["rabat"] = round(p.rabat * p.ilosc, 2)
        linia["wartosc"] = round(p.cena_po_rabacie * p.ilosc, 2)
        linia_brutto = p.cena_po_rabacie * p.ilosc
        linia_netto = linia_brutto / (1 + p.vat)
        linia_vat = linia_brutto - linia_netto
        suma_brutto = suma_brutto + linia_brutto
        suma_netto = suma_netto + linia_netto
        suma_vat = suma_vat + linia_vat
        suma_rabat = suma_rabat + p.rabat * p.ilosc
        paragon["linie"].append(linia)
    paragon["suma_brutto"] = round(suma_brutto, 2)
    paragon["suma_netto"] = round(suma_netto, 2)
    paragon["suma_vat"] = round(suma_vat, 2)
    paragon["koszt_dostawy"] = round(koszt_dostawy, 2)
    paragon["oszczednosc"] = round(suma_rabat, 2)
    paragon["do_zaplaty"] = round(suma_brutto + koszt_dostawy, 2)
    paragon["klient_id"] = klient.id
    return paragon

def wydrukuj_paragon(paragon):
    print("=" * 50)
    print("PARAGON FISKALNY")
    print("=" * 50)
    print(f"Klient: {paragon['klient_id']}")
    print("-" * 50)
    for l in paragon["linie"]:
        print(f"{l['nazwa']} ({l['sku']}) x{l['ilosc']}")
        print(f"  Cena: {l['cena_przed']:.2f} -> {l['cena_po']:.2f} PLN (rabat: {l['rabat']:.2f} PLN)")
        print(f"  Wartosc: {l['wartosc']:.2f} PLN")
    print("-" * 50)
    print(f"Suma brutto: {paragon['suma_brutto']:.2f} PLN")
    print(f"Suma netto:  {paragon['suma_netto']:.2f} PLN")
    print(f"VAT:         {paragon['suma_vat']:.2f} PLN")
    print(f"Dostawa:     {paragon['koszt_dostawy']:.2f} PLN")
    print(f"Oszczedziles: {paragon['oszczednosc']:.2f} PLN")
    print("=" * 50)
    print(f"DO ZAPLATY: {paragon['do_zaplaty']:.2f} PLN")
    print("=" * 50)

def oblicz_koszyk(produkty, klient, promocje):
    waliduj_wejscie(produkty, klient, promocje)

    uzyto_2plus1 = False
    koszt_dostawy = 15.0

    for promo in promocje:
        if promo.aktywna == True and promo.typ == "procent":
            produkty = zastosuj_procent(produkty, promo)

    for promo in promocje:
        if promo.aktywna == True and promo.typ == "2plus1":
            produkty, czy_uzyto = zastosuj_2plus1(produkty, promo)
            if czy_uzyto == True:
                uzyto_2plus1 = True

    for promo in promocje:
        if promo.aktywna == True and promo.typ == "najtanszy_50":
            produkty = zastosuj_najtanszy_50(produkty, promo)

    for promo in promocje:
        if promo.aktywna == True and promo.typ == "kupon":
            produkty = zastosuj_kupon(produkty, promo, uzyto_2plus1)

    for promo in promocje:
        if promo.aktywna == True and promo.typ == "darmowa_dostawa":
            koszt_dostawy = oblicz_dostawe(produkty, promo)

    paragon = generuj_paragon(produkty, klient, koszt_dostawy)
    return paragon


if __name__ == "__main__":
    p1 = Produkt("BOOK-SF-1", "Diuna", "books", 49.99, 0.05, 2)
    p2 = Produkt("CLOTH-1", "Koszulka", "clothes", 89.99, 0.23, 3)
    p3 = Produkt("OD-NAVY-S", "Ocean Dynamics", "clothes", 120.00, 0.23, 1)
    p4 = Produkt("OUTLET-1", "Stara kurtka", "outlet", 199.99, 0.23, 1)

    klient = Klient("K001", "gold")

    promo1 = Promocja("procent", 15, kategoria="books")
    promo2 = Promocja("2plus1", 0, sku_lista=["CLOTH-1"])
    promo3 = Promocja("darmowa_dostawa", 0, prog=200)
    promo4 = Promocja("kupon", 20, prog=100, kupon_kod="RABAT20")
    promo5 = Promocja("najtanszy_50", 50, kategoria="clothes")

    koszyk = [p1, p2, p3, p4]
    paragon = oblicz_koszyk(koszyk, klient, [promo1, promo2, promo3, promo4, promo5])
    wydrukuj_paragon(paragon)
