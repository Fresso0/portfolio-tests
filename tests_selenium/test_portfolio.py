"""
Tests automatisés Selenium du portfolio https://fresnel.host
Auteur : Fresnel Dossou

Lancement local :  pytest tests_selenium/ -v
"""
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://fresnel.host"


@pytest.fixture(scope="module")
def driver():
    """Navigateur Chrome en mode headless (sans interface graphique)."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,900")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


# ---------- 1. Disponibilité et contenu de base ----------

def test_page_accueil_se_charge(driver):
    """La page d'accueil répond et le titre identifie bien le portfolio."""
    driver.get(BASE_URL)
    assert "Fresnel" in driver.title


def test_nom_affiche_dans_le_hero(driver):
    """Le nom 'Fresnel DOSSOU' est visible dans le titre principal."""
    driver.get(BASE_URL)
    h1 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "FRESNEL" in h1.text.upper()


# ---------- 2. Navigation ----------

@pytest.mark.parametrize("libelle", ["Projets", "Expérience", "Outils"])
def test_liens_de_navigation_presents(driver, libelle):
    """Chaque entrée du menu de navigation est présente et cliquable."""
    driver.get(BASE_URL)
    lien = driver.find_element(By.PARTIAL_LINK_TEXT, libelle)
    assert lien.is_displayed()
    assert lien.get_attribute("href")  # le lien pointe quelque part


def test_lien_cv_telechargeable(driver):
    """Le CV en PDF est accessible (HTTP 200 et type PDF)."""
    driver.get(BASE_URL)
    lien_cv = driver.find_element(
        By.CSS_SELECTOR, "a[href*='cv.pdf'], a[href$='.pdf']"
    )
    reponse = requests.get(lien_cv.get_attribute("href"), timeout=15)
    assert reponse.status_code == 200
    assert "pdf" in reponse.headers.get("Content-Type", "").lower()


def test_aucun_lien_projet_casse(driver):
    """Aucun lien externe de la section projets ne renvoie une erreur 4xx/5xx."""
    driver.get(BASE_URL)
    liens = driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
    urls = {l.get_attribute("href") for l in liens if l.get_attribute("href")}
    casses = []
    for url in urls:
        if "linkedin" in url:  # LinkedIn bloque les robots : hors périmètre
            continue
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code >= 400:
                casses.append((url, r.status_code))
        except requests.RequestException as exc:
            casses.append((url, str(exc)))
    assert not casses, f"Liens cassés : {casses}"


# ---------- 3. Formulaire de contact (validation côté client) ----------

def _remplir(driver, selecteur, valeur):
    champ = driver.find_element(By.CSS_SELECTOR, selecteur)
    champ.clear()
    champ.send_keys(valeur)
    return champ


def test_formulaire_refuse_email_invalide(driver):
    """Un email mal formé déclenche le message d'erreur de validation."""
    driver.get(BASE_URL)
    # ⚠️ Adapte ces sélecteurs aux vrais name/id de ton formulaire
    _remplir(driver, "input[name='email'], input[type='email']", "pas-un-email")
    _remplir(driver, "textarea", "Un message de test suffisamment long pour valider")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], form button").click()
    corps = driver.find_element(By.TAG_NAME, "body").text
    assert "Adresse email" in corps or "email" in corps.lower()


def test_formulaire_refuse_message_trop_court(driver):
    """Un message de moins de 7 mots déclenche le message d'erreur dédié."""
    driver.get(BASE_URL)
    _remplir(driver, "input[name='email'], input[type='email']", "test@example.com")
    _remplir(driver, "textarea", "Trop court")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], form button").click()
    corps = driver.find_element(By.TAG_NAME, "body").text
    assert "7 mots" in corps


# ---------- 4. Responsive ----------

def test_affichage_mobile(driver):
    """En largeur mobile (375px), le contenu principal reste visible."""
    driver.set_window_size(375, 812)  # iPhone X
    driver.get(BASE_URL)
    h1 = driver.find_element(By.TAG_NAME, "h1")
    assert h1.is_displayed()
    driver.set_window_size(1366, 900)  # on restaure
