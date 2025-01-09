import numpy as np
import eurocodepy as ec

antwoord = input("Is het een q-last op twee steunpunten?")
if antwoord == "ja" or antwoord == "Ja" or antwoord == "JA":
    q = float(input("Geef de q-last in kn/m:"))
    Lm = float(input("Geef de lengte in m:"))
    Lmm = Lm * 1e3
    print(" ")

    Med = 1/8 * (q * Lm**2)

    Ved = 1/2 * (q * Lm)

    print(f"De maximale verticale belasting is {Ved} kN")
    print(f"Het maximale moment is {Med} kNm")

else:
    print("Dan moet Ved en Med zelf berekend worden.")
    print(" ")
    Ved = input("Wat is je Ved")
    Med = input("Wat is je Med")

    # Gegevens uitvragen 

steel_profiles = ec.dbase.SteelProfiles

# Profiel uitvragen
profiel = str(input("Geef je profiel (bijvoorbeeld IPE200): "))
print(" ")

# Profiel opvragen
profile_data = getattr(steel_profiles.Euro.I_SECTION, profiel)

# Gegevens profiel opvragen
A = profile_data.A
Iz = profile_data.I22
Iy = profile_data.I33
b = profile_data.BF
h = profile_data.D
Tw = profile_data.TW
Tf = profile_data.TF

# Radius bepalen (dit staat niet in de database :/ )
def radius(profiel):
    if profiel in ["IPE100", "IPE120", "IPE140"]:
        r = 7
    elif profiel in ["IPE160", "IPE180"]:
        r = 9
    elif profiel in ["IPE200", "IPE200"]:
        r = 12
    elif profiel in ["IPE240", "IPE270, IPE300"]:
        r = 15
    elif profiel in ["IPE330", "IPE360"]:
        r = 18
    elif profiel in ["IPE400", "IPE450, IPE500"]:
        r = 21
    else:
        r = 24
    return(r)

r = radius(profiel)

print(r)

Cf = (float(b) - (2*r) - (float(Tw)) / 2)
Cw = float(h) - (2 * float(Tf)) - 2*r

print(f"Oppervlakte van het {profiel}-profiel: {A} mm²")
print(f"Iz van het {profiel}-profiel: {Iz} mm⁴")
print(f"Iy van het {profiel}-profiel: {Iy} mm⁴")
print(f"Hoogte van het {profiel}-profiel: {h} mm")
print(f"Breedte van het {profiel}-profiel: {b} mm")
print(" ")
print(f"Lijfdikte van het {profiel}-profiel: {Tw} mm")
print(f"Flensdikte van het {profiel}-profiel: {Tf} mm")
print(f"C-flens van het {profiel}-profiel: {Cf} mm")
print(f"C-lijf van het {profiel}-profiel: {Cw} mm")
print(" ")

    # Doorsnedeklassen

print(f"Doorsnedeklassen berekend voor het {profiel}-profiel:")
print(" ")

def doorsnedeklasse_flens(t_f, c_f):
    t_f = float(t_f)
    c_f = float(c_f)
    verhouding  = c_f / t_f
    if verhouding <= 9:
        doorsnedeklasse_flens  = 1
    elif verhouding <= 10:
        doorsnedeklasse_flens = 2
    else:
        doorsnedeklasse_flens = 3
    return(doorsnedeklasse_flens)

print(f"De doorsnedeklasse van de flens is: {doorsnedeklasse_flens(Tf, Cf)}")
    

def doorsnedeklasse_lijf(t_w, c_w):
    t_w = float(t_w)
    c_w = float(c_w)
    verhouding  = c_w / t_w
    if verhouding <= 72:
        doorsnedeklasse_lijf  = 1
    elif verhouding <= 84:
        doorsnedeklasse_lijf = 2
    else:
        doorsnedeklasse_lijf = 3
    return(doorsnedeklasse_lijf)

print(f"De doorsnedeklasse van het lijf is: {doorsnedeklasse_lijf(Tw, Cw)}")
print(" ")

def dsk(doorsnedeklasse_flens, doorsnedeklasse_lijf):
    if doorsnedeklasse_flens <= doorsnedeklasse_lijf:
        dsk = doorsnedeklasse_lijf
    else:
        dsk = doorsnedeklasse_flens

    return(dsk)

dsk = dsk(doorsnedeklasse_flens(Tf, Cf), doorsnedeklasse_lijf(Tw,Cw))

print(f"Dus de doorsnedeklasse van het profiel is {dsk}")

print(" ")

    # Toetsingen Med.

Fyd = 235
y0 = 1



if dsk == 1:
    Wpl = profile_data.Z33
    print(f"Er mag met het plastische momentweerstand: {Wpl} mm³ gerekend worden,")

    Mcrd = (float(Wpl) * float(Fyd)) / float(y0)
    Mcrd2 = float(Mcrd)*1e-6
    print(f"de rekenwaarde van de momentweerstand capaciteit is {Mcrd} Nmm en dus {Mcrd2} kNm.")
    print(" ")
    
else:
    Wel = profile_data.S33POS
    print(f"Er mag met het elastische momentweerstand: {Wel} gerekend worden")

    Mcrd = (float(Wel) * float(Fyd)) / float(y0)
    Mcrd2 = float(Mcrd)*1e-6
    print(f"De rekenwaarde van de momentweerstand capaciteit is {Mcrd}")

UCm = round(float(Med)/float(Mcrd2),2)

if UCm < 1:
    print(f"De Unitycheck is: {UCm}, het {profiel}-profiel voldoet dus voor het maximale moment.")
else:
    print(f"De Unitycheck is: {UCm}, het {profiel}-profiel voldoet dus voor het maximale moment niet.")

print(" ")

# Toetsingen Ved.

if dsk == 1:
    print("Er mag plastisch bepaald worden,")
    Av = float(A) - (2 * float(b) * float(Tf)) + ((float(Tw) + (2 * r))*float(Tf))
    Vcrd = round(((Av * Fyd)/np.sqrt(3))/y0, 2)
    Vcrd2 = round(float(Vcrd)*1e-3, 2)
    print(f"de rekenwaarde van de momentweerstand capaciteit is {Vcrd} N en dus {Vcrd2} kN.")
    print(" ")

else:
    print("Het mag elastisch bepaald worden,")
    Aw = (float(h) - (2 * float(Tf)) * Tw)
    Vcrd = round(((Aw * Fyd)/np.sqrt(3))/y0, 2)
    Vcrd2 = round(float(Vcrd)*1e-3, 2)

UCv = round(float(Ved)/float(Vcrd2),2)

if UCv < 1:
    print(f"De Unitycheck is: {UCv}, het {profiel}-profiel voldoet dus voor de maximale verticale kracht.")
else:
    print(f"De Unitycheck is: {UCv}, het {profiel}-profiel voldoet dus voor de maximale verticale kracht niet.")

print(" ")

if UCm < 1 and UCv < 1:
    print(f"Beide unitychecks ({UCm}), ({UCv}) zijn kleiner dan 1, de balk voldoet dus.")

elif UCm >= 1:
    print(f"De unitycheck voor het maximale moment ({UCm}) voldoet niet, probeer een groter profiel.")

else:
    print(f"De unitycheck voor de maximale verticale kracht ({UCv}) voldoet niet, probeer een groter profiel.")
