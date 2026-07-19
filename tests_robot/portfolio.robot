*** Settings ***
Documentation     Tests d'acceptance du portfolio fresnel.host avec Robot Framework.
...               Lancement :  robot -d resultats tests_robot/
Library           SeleniumLibrary
Suite Setup       Ouvrir Le Portfolio
Suite Teardown    Close All Browsers

*** Variables ***
${URL}            https://fresnel.host
${NAVIGATEUR}     headlesschrome

*** Keywords ***
Ouvrir Le Portfolio
    Open Browser    ${URL}    ${NAVIGATEUR}
    ...    options=add_argument("--no-sandbox"); add_argument("--disable-dev-shm-usage")
    Set Window Size    1366    900

*** Test Cases ***
La Page D'Accueil S'Affiche
    [Documentation]    Le titre de l'onglet identifie le portfolio.
    Title Should Contain    Fresnel

Le Nom Est Visible Dans Le Hero
    [Documentation]    Le h1 principal contient le nom du propriétaire.
    Wait Until Element Is Visible    tag:h1    timeout=10s
    Element Should Contain    tag:h1    Fresnel

Le Menu De Navigation Est Complet
    [Documentation]    Les entrées principales du menu sont présentes.
    Page Should Contain Link    partial link:Projets
    Page Should Contain Link    partial link:Expérience
    Page Should Contain Link    partial link:Outils

La Section Projets Liste Les Réalisations
    [Documentation]    Les projets phares apparaissent sur la page.
    Page Should Contain    Labellisation
    Page Should Contain    Morpion

Le Formulaire Refuse Un Message Trop Court
    [Documentation]    La règle « 7 mots minimum » est bien appliquée.
    Input Text    css:input[type='email']    test@example.com
    Input Text    css:textarea               Trop court
    Click Element    css:form button
    Page Should Contain    7 mots
