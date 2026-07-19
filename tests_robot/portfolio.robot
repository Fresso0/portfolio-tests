*** Settings ***
Documentation     Tests d'acceptance du portfolio fresnel.host (SPA) avec Robot Framework.
...               Lancement :  robot -d resultats tests_robot/
Library           SeleniumLibrary
Test Setup        Ouvrir Le Portfolio
Test Teardown     Close All Browsers

*** Variables ***
${URL}            https://fresnel.host
${NAVIGATEUR}     headlesschrome

*** Keywords ***
Ouvrir Le Portfolio
    Open Browser    ${URL}    ${NAVIGATEUR}
    ...    options=add_argument("--no-sandbox"); add_argument("--disable-dev-shm-usage")
    Set Window Size    1366    900
    Wait Until Element Is Visible    tag:h1    timeout=10s

Aller Au Formulaire De Contact
    Execute Javascript    document.getElementById('contact').scrollIntoView();

Soumettre Le Formulaire
    Execute Javascript    document.querySelector('#contactForm .send').click();
    
*** Test Cases ***
La Page D'Accueil S'Affiche
    [Documentation]    Le titre de l'onglet identifie le portfolio.
    ${titre}=    Get Title
    Should Contain    ${titre}    Fresnel

Le Nom Est Visible
    [Documentation]    Le h1 de la carte profil contient le nom du propriétaire.
    Element Should Contain    tag:h1    Fresnel

La Navigation SPA Affiche La Vue Projets
    [Documentation]    Cliquer l'onglet Projets rend la section #projets visible.
    Click Element    css:.topnav [data-goto='projets']
    Wait Until Element Is Visible    id:projets    timeout=10s
    Page Should Contain    Labellisation

La Navigation SPA Affiche La Vue Outils
    [Documentation]    Cliquer l'onglet Outils rend la section #outils visible.
    Click Element    css:.topnav [data-goto='outils']
    Wait Until Element Is Visible    id:outils    timeout=10s

Le Formulaire Refuse Un Email Invalide
    [Documentation]    Un email mal formé rend visible l'erreur du champ email.
    Aller Au Formulaire De Contact
    Input Text    id:name     Testeur
    Input Text    id:email    pas-un-email
    Input Text    id:msg      Ceci est un message assez long pour être valide
    Execute Javascript    document.querySelector('#contactForm .send').click();
    Wait Until Element Is Visible    css:#fEmail .ferr    timeout=5s

Le Formulaire Refuse Un Message Trop Court
    [Documentation]    La règle « 7 mots minimum » rend visible l'erreur du message.
    Aller Au Formulaire De Contact
    Input Text    id:name     Testeur
    Input Text    id:email    test@example.com
    Input Text    id:msg      Trop court
    Soumettre Le Formulaire
    Wait Until Element Is Visible    css:#fMsg .ferr    timeout=5s