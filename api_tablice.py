import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
import re
import pandas as pd

def pretrazi_firme(kljucna_rijec, broj_rezultata=10):
    service = build("customsearch", "v1", developerKey="AIzaSyClPVkLCOAKCyJzPp0ryLkQnskJ4p3WS1Y")
    firme = []
    num_results_per_query = 10  # Maksimalno 10 rezultata po zahtjevu
    
    for start_index in range(1, broj_rezultata + 1, num_results_per_query):
        try:
            rezultati = service.cse().list(q=kljucna_rijec, cx="24152216f693b48c2", start=start_index, num=num_results_per_query).execute()
            for item in rezultati.get('items', []):
                url = item['link']
                try:
                    response = requests.get(url, timeout=10, verify=False)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Pronalazi naslov
                    naslov = soup.find('title').text if soup.find('title') else "Naslov nije pronađen"
                    
                    # Pronalazi e-adrese
                    emaili = find_emails(response.text)
                    
                    firme.append({'URL': url, 'Naslov': naslov, 'E-pošta': ', '.join(emaili)})
                
                except requests.exceptions.SSLError as e:
                    print(f"SSL greška pri obradi URL-a {url}: {e}")
                except requests.exceptions.ConnectionError as e:
                    print(f"Povezivanje prekinuto pri obradi URL-a {url}: {e}")
                except requests.exceptions.TooManyRedirects as e:
                    print(f"Previše preusmjeravanja za URL {url}: {e}")
                except requests.exceptions.RequestException as e:
                    print(f"Greška pri obradi URL-a {url}: {e}")
        
        except Exception as e:
            print(f"Greška pri izvođenju pretrage: {e}")
    
    return firme

def find_emails(text):
    # Koristi regularni izraz za pronalazak e-adresa
    pattern = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(pattern, text)
    return emails

def spremi_u_csv(podaci, naziv_datoteke):
    df = pd.DataFrame(podaci)
    df.to_csv(naziv_datoteke, index=False)
    print(f"Podaci su spremljeni u {naziv_datoteke}")

if __name__ == "__main__":
    kljucna_rijec = "građevinska firma"
    broj_rezultata = 200 # Promijenite ovo u željeni broj rezultata
    firme = pretrazi_firme(kljucna_rijec, broj_rezultata)
    
    for firma in firme:
        print(f"URL: {firma['URL']}")
        print(f"Naslov: {firma['Naslov']}")
        print(f"E-pošta: {firma['E-pošta'] if firma['E-pošta'] else 'Nema dostupnih e-adresa'}")
        print("-" * 40)
    
    spremi_u_csv(firme, 'firme.csv')
