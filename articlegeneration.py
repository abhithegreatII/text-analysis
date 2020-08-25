import math as m
import pandas as pd
import re
from nltk.tokenize import word_tokenize


def write_txt_file(city, titel, a):
    """function that writes each article as .txt file"""
    with open(f"generatedTexts/{city} Kriminalität.txt", "w+") as f:
        f.write(titel + a)

def append_txt_file(city, c):
    """appending existing file with new paragraphs"""
    with open(f"generatedTexts/{city} Kriminalität.txt", "a+") as f:
        f.write(c)

def extract_df_values(df, city, delikt, monat, fall):
    """extracting values that are needed for the template"""
    return df.loc[(df.Behörde == city) & (df.Delikt == delikt) & (df.Monat == monat), fall].item()

def calc_percent_delikt(df, fall, newcolname):
    """for each delikt the function finds the percantage change and creates a new column"""
    df_diff = df.groupby(['Behörde', 'Delikt'])[fall].diff()
    df[newcolname] = (df_diff / df[fall])*(-100)


df = pd.read_csv("./KriminalitatsstatistikNRW.csv", encoding = "latin1", quotechar= '"')  # sep by comma 

for i in df.columns:
    print(df[i].isnull().values.any())  # check columns for Na

# filtering by right month and year
df_1819 = df[(df.Monat == "Oktober 2019")  | (df.Monat == "Oktober 2018")]

# finding percentage for each "delikt" with (versuche in 2019 - versuch in 2018) / versuch in 2019
calc_percent_delikt(df_1819, 'bekanntgewordene Fälle', '%/fälle')
calc_percent_delikt(df_1819, 'davon Versuche', '%/versuch')
calc_percent_delikt(df_1819, 'Aufklärungsquote in %', '%/gelöst')

# jeder x-te Fall, fall / aufklärung
df_1819['x-te'] = (df_1819['bekanntgewordene Fälle'] / df_1819['Aufklärungsquote in %'])


b = ''
for j in range(len(df_1819)):
    if b == df_1819.iloc[j][0]:
        continue  # iterating over unique names of city, skipping if city already done
    else:
        city = df_1819.iloc[j][0]
        city_df = df_1819.loc[df_1819.Behörde == city]

        # extracting all necessary values to insert into template
        if not m.isnan((df_1819.loc[(df_1819.Behörde == city) & (df_1819.Delikt == 'Tageswohnungs-einbruchdiebstahl') & (df_1819.Monat == 'Oktober 2019'), 'bekanntgewordene Fälle'].item())):
            tageseinbruch = extract_df_values(df_1819, city, 'Tageswohnungs-einbruchdiebstahl', 'Oktober 2019', 'bekanntgewordene Fälle')
        wohnungseinbruchdiebstahl = extract_df_values(df_1819, city, 'Wohnungseinbruchdiebstahl', 'Oktober 2019', 'bekanntgewordene Fälle')

        versuche = extract_df_values(df_1819, city, 'Einbruchdelikte', 'Oktober 2019', 'davon Versuche')
        prozentfall = extract_df_values(df_1819, city, 'Einbruchdelikte', 'Oktober 2018', '%/fälle')
        prozentversuch = extract_df_values(df_1819, city, 'Einbruchdelikte', 'Oktober 2018', '%/versuch')
        xte = extract_df_values(df_1819, city, 'Einbruchdelikte', 'Oktober 2019', 'x-te')
        funfjahrfall = extract_df_values(df, city, 'Einbruchdelikte', 'Oktober 2014', 'bekanntgewordene Fälle')

        raubstrasse = extract_df_values(df_1819, city, 'Raubüberfälle auf Straßen, Wegen oder Plätzen', 'Oktober 2019', 'bekanntgewordene Fälle')
        raubstrasse18 = extract_df_values(df_1819, city, 'Raubüberfälle auf Straßen, Wegen oder Plätzen', 'Oktober 2018', 'bekanntgewordene Fälle')
        raubstrasse14 = extract_df_values(df, city, 'Raubüberfälle auf Straßen, Wegen oder Plätzen', 'Oktober 2014', 'bekanntgewordene Fälle')
        taschendiebstahl = extract_df_values(df_1819, city, 'Taschendiebstahl', 'Oktober 2019', 'bekanntgewordene Fälle')
        fahrraddiebstahl = extract_df_values(df_1819, city, 'Diebstahl von Fahrrädern', 'Oktober 2019', 'bekanntgewordene Fälle')

        # inserting calculated and extracted values into the template
        titel = f"In {city} geht die Zahl der Einbrüche weiter zurück!\n \n"
        a = (f"Im September diesen Jahres gab es in {city} {int(tageseinbruch) + int(wohnungseinbruchdiebstahl)} Wohnungseinbrüche und {int(versuche)} Mal wurde versucht, in eine Wohnung oder ein Haus einzubrechen. \n" \
        f"Blickt man auf das vorherige Jahr dann wird weniger häufig eingebrochen: um {int(prozentfall)}% ging die Zahl der Einbrüche innerhalb der vergangenen 12 Monate zurück, die Zahl der versuchten Einbrüche (sogar) um {int(prozentversuch)} Prozent. Leider wurden nicht mehr Einbrücke aufgeklärt als im Vorjahr: jeder {int(xte)}-te Fall konnte von der Polizei aufgeklärt werden. Vor 5 Jahren {int(funfjahrfall)}.\n" \
        f"Die grösste Angst haben viele Menschen davor, auf einmal am hellichten Tag in ihrer Wohnung von einem Einbrecher überrascht zu werden. Deswegen werden diese sogenannten „Tageseinbrüche“ von der Polizei auch extra in einer Statistik erfasst. Tagsüber gab es in {city} im September {int(tageseinbruch)} Einbrüche mitten am Tag \n"
        )

        # creating .txt file
        write_txt_file(city, titel, a)

        # appending an article paragraph if necessary
        if not m.isnan(raubstrasse) and not m.isnan(raubstrasse18) and not m.isnan(raubstrasse14) :
            c = f"\nÜberfallen werden auf der Straße – ein andere große Angst vieler Bewohner auch in {city}. Die Straftat, die offiziell unter „Raubüberfälle auf Straßen, Wegen und Plätzen“ heisst, wurde {int(raubstrasse)} mal von der Polizei aufgenommen. Vor einem jahr {int(raubstrasse18)} mal. Vor 5 jahr {int(raubstrasse14)}." \
                f"\nAndere Straftaten auf öffentlichen Wegen, also zum Beispiel Betrug, Taschendiebstahl oder Fahrraddiebstahl wurden {int(taschendiebstahl + fahrraddiebstahl)} mal registriert."
            
            append_txt_file(city, c)

        b = city  # keep track of which city we are iterating over
        print(city, "file has been created")

