from .Itemset import Itemset


def itemsets1(transactions, min_supp):
    # leere Abbildung anlegen
    C1 = {}

    # alle Transaktionen durchgehen
    for _, items in transactions:
        # alle Elemente der Transaktion betrachten
        for element in items:
            # Element zur Abbildung hinzufügen
            # bzw. Anzahl um 1 erhöhen
            if element not in C1:
                C1[element] = 1
            else:
                C1[element] += 1

    # Elemente nach minimalem Support filtern
    # und in Itemset umwandeln
    return set(Itemset(item) for item, count in C1.items()
               if count / len(transactions) >= min_supp)


def generiere_kandidaten(L, k):
    # Join
    all_C_k = set()

    for e1 in L:
        for e2 in L:
            if e1.matches(e2, k - 2):
                all_C_k.add(e1.union(e2))

    # Pruning
    C_k = set()

    for c in all_C_k:
        for subset in c.subsets(k - 1):
            if subset not in L:
                break
        else:
            C_k.add(c)

    return C_k


def filtere_kandidaten(C_k, transactions, min_supp):
    return set(c for c in C_k if c.support_in(transactions) >= min_supp)


def apriori(transactions, min_supp, min_size=0):
    # Liste der L_k anlegen
    # mit leerer Menge als Padding
    Ls = [set(), itemsets1(transactions, min_supp)]

    # k initialisieren
    k = 2

    # Schleife
    while len(Ls[-1]) > 0:
        # Kandidatengenerierung und Filter
        C_k = generiere_kandidaten(Ls[-1], k)
        L_k = filtere_kandidaten(C_k, transactions, min_supp)

        # L_k ablegen
        Ls.append(L_k)

        # k zählen
        k += 1

    # Vereinigung bilden
    result = set()
    for L in Ls:
        for i in L:
            if len(i) >= min_size:
                result.add(i)

    return result
