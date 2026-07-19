"""
Tests automatisés Selenium du portfolio https://fresnel.host
Auteur : Fresnel Dossou

Particularité du site : c'est une SPA maison — les sections s'affichent via
des attributs data-views et une classe .show ; la navigation utilise des
<a data-goto> sans href, pilotés en JavaScript. Les sélecteurs ci-dessous
ciblent les vrais id/classes du site (#email, #msg, .send, .topnav...).

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


@pytest.fixture()
def driver():
    """Chrome headless, une session neuve par test (la SPA garde un état)."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,900")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    drv.get(BASE_URL)
    yield drv
    drv.quit()


# ---------- 1. Disponibilité et contenu de base ----------

def test_titre_de_la_page(driver):
    """Le titre de l'onglet identifie bien le portfolio."""
    assert "Fresnel" in driver.title


def test_nom_affiche(driver):
    """Le nom 'Fresnel DOSSOU' est visible (carte profil)."""
    h1 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "FRESNEL" in h1.text.upper()


# ---------- 2. Navigation SPA ----------

@pytest.mark.parametrize("vue", ["projets", "experience", "outils"])
def test_navigation_change_de_vue(driver, vue):
    """Cliquer un onglet du menu affiche la section correspondante (SPA)."""
    onglet = driver.find_element(By.CSS_SELECTOR, f".topnav [data-goto='{vue}']")
    onglet.click()
    section = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, vue))
    )
    assert "show" in section.get_attribute("class")


def test_lien_cv_telechargeable(driver):
    """Le CV en PDF est accessible (HTTP 200 et type PDF)."""
    lien_cv = driver.find_element(By.CSS_SELECTOR, "a[href*='cv.pdf']")
    reponse = requests.get(lien_cv.get_attribute("href"), timeout=15)
    assert reponse.status_code == 200
    assert "pdf" in reponse.headers.get("Content-Type", "").lower()


def test_aucun_lien_externe_casse(driver):
    """Aucun lien externe (projets, réseaux) ne renvoie une erreur 4xx/5xx."""
    liens = driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
    urls = {l.get_attribute("href") for l in liens if l.get_attribute("href")}
    casses = []
    for url in urls:
        if "linkedin" in url:  # LinkedIn bloque les robots : hors périmètre
            continue
        try:
            r = requests.get(url, timeout=10, allow_redirects=True, stream=True)
            if r.status_code >= 400:
                casses.append((url, r.status_code))
            r.close()
        except requests.RequestException as exc:
            casses.append((url, str(exc)))
    assert not casses, f"Liens cassés : {casses}"


# ---------- 3. Formulaire de contact (validation côté client) ----------

def _remplir_formulaire(driver, nom, email, message):
    driver.execute_script(
        "document.getElementById('contact').scrollIntoView();"
    )
    driver.find_element(By.ID, "name").send_keys(nom)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "msg").send_keys(message)
    driver.execute_script(
        "document.querySelector('#contactForm .send').click();"
    )


def test_formulaire_refuse_email_invalide(driver):
    """Un email mal formé ajoute la classe .invalid et affiche l'erreur dédiée."""
    _remplir_formulaire(
        driver, "Testeur", "pas-un-email",
        "Ceci est un message de test suffisamment long pour valider",
    )
    champ_email = driver.find_element(By.ID, "fEmail")
    WebDriverWait(driver, 5).until(
        lambda d: "invalid" in champ_email.get_attribute("class")
    )
    erreur = champ_email.find_element(By.CSS_SELECTOR, ".ferr")
    assert erreur.is_displayed()
    assert "email" in erreur.text.lower()


def test_formulaire_refuse_message_trop_court(driver):
    """Un message de moins de 7 mots ajoute .invalid et affiche l'erreur dédiée."""
    _remplir_formulaire(driver, "Testeur", "test@example.com", "Trop court")
    champ_msg = driver.find_element(By.ID, "fMsg")
    WebDriverWait(driver, 5).until(
        lambda d: "invalid" in champ_msg.get_attribute("class")
    )
    erreur = champ_msg.find_element(By.CSS_SELECTOR, ".ferr")
    assert erreur.is_displayed()
    assert "7 mots" in erreur.text


def test_compteur_de_mots_se_met_a_jour(driver):
    """Le compteur x/7 reflète le nombre de mots saisis dans le message."""
    driver.execute_script("document.getElementById('contact').scrollIntoView();")
    driver.find_element(By.ID, "msg").send_keys("un deux trois")
    compteur = driver.find_element(By.ID, "wc")
    WebDriverWait(driver, 5).until(lambda d: compteur.text == "3")
    assert compteur.text == "3"


def test_email_corrige_retire_l_erreur(driver):
    """Corriger l'email en direct retire la classe .invalid (validation live)."""
    _remplir_formulaire(
        driver, "Testeur", "mauvais",
        "Ceci est un message de test suffisamment long pour valider",
    )
    champ_email = driver.find_element(By.ID, "fEmail")
    WebDriverWait(driver, 5).until(
        lambda d: "invalid" in champ_email.get_attribute("class")
    )
    driver.find_element(By.ID, "email").send_keys("@example.com")  # devient valide
    WebDriverWait(driver, 5).until(
        lambda d: "invalid" not in champ_email.get_attribute("class")
    )


# ---------- 4. Responsive ----------

def test_affichage_mobile(driver):
    """En largeur mobile (375px), le hero et la nav mobile restent visibles."""
    driver.set_window_size(375, 812)
    driver.get(BASE_URL)
    hero = driver.find_element(By.CSS_SELECTOR, ".hero-title")
    assert hero.is_displayed()
    nav_mobile = driver.find_element(By.CSS_SELECTOR, ".bottomnav")
    assert nav_mobile.is_displayed()
