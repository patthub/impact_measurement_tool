import requests
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm


# Podstawowe zapytanie do usługi pracownicy
response = requests.get("https://radon.nauka.gov.pl/opendata/polon/employees", params={'resultNumbers': 1})
print(response.json()['results'][0]['personalData'])




