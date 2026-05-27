import sys
from crypto_utils import generer_cles
from signalement import (
    soumettre_signalement,
    consulter_signalement,
    lister_signalements,
    mettre_a_jour_statut
)
from auditeur import (
    afficher_journal,
    verifier_journal,
    exporter_journal
)
from audit import enregistrer_action

def afficher_menu_principal():
    print("\n" + "="*55)
    print("           ZEROTRACE — Système de signalement")
    print("           anonyme à protection cryptographique")
    print("="*55)
    print("  Choisissez votre profil :\n")
    print("  [1] 🕵️  Lanceur d'alerte — Soumettre un signalement")
    print("  [2] 🔍  Enquêteur       — Gérer les dossiers")
    print("  [3] 📋  Auditeur        — Consulter le journal")
    print("  [0] 🚪  Quitter")
    print("="*55)

def menu_lanceur():
    print("\n" + "-"*55)
    print("  MODE : LANCEUR D'ALERTE")
    print("-"*55)
    print("  [1] Soumettre un nouveau signalement")
    print("  [2] Suivre mon dossier (via token)")
    print("  [0] Retour")
    print("-"*55)

    choix = input("  Votre choix : ").strip()

    if choix == "1":
        print("\n  Catégories disponibles :")
        print("  [1] Corruption / Détournement de fonds")
        print("  [2] Fraude académique")
        print("  [3] Abus de pouvoir")
        print("  [4] Trafic de substances illicites")
        print("  [5] Autre")

        cat_choix = input("\n  Choisissez une catégorie : ").strip()
        categories = {
            "1": "Corruption / Détournement de fonds",
            "2": "Fraude académique",
            "3": "Abus de pouvoir",
            "4": "Trafic de substances illicites",
            "5": "Autre"
        }
        categorie = categories.get(cat_choix, "Autre")

        print("\n  Décrivez les faits (appuyez sur Entrée quand terminé) :")
        contenu = input("  > ").strip()

        if contenu:
            token = soumettre_signalement(categorie, contenu)
            print(f"\n  ⚠️  IMPORTANT : Conservez précieusement votre token !")
            print(f"  Il est votre seule clé d'accès anonyme à ce dossier.\n")
        else:
            print("  ❌ Contenu vide — signalement annulé.")

    elif choix == "2":
        token = input("\n  Entrez votre token : ").strip()
        if token:
            signalement = consulter_signalement(token)
            if signalement:
                print("\n" + "-"*55)
                print(f"  📁 Dossier trouvé")
                print(f"  Catégorie  : {signalement['categorie']}")
                print(f"  Date       : {signalement['horodatage']}")
                print(f"  Statut     : {signalement['statut']}")
                print(f"  Contenu    : {signalement['contenu']}")
                print("-"*55)

def menu_enqueteur():
    print("\n" + "-"*55)
    print("  MODE : ENQUÊTEUR")
    print("-"*55)
    print("  Authentification requise.")

    # Authentification simple pour le Sprint Alpha
    mot_de_passe = input("  Mot de passe enquêteur : ").strip()

    # Mot de passe hardcodé pour le sprint Alpha
    # (sera remplacé par bcrypt + TOTP au Sprint Beta)
    if mot_de_passe != "enqueteur2026":
        print("  ❌ Mot de passe incorrect.")
        enregistrer_action(
            acteur="INCONNU",
            action="TENTATIVE_CONNEXION_ECHOUEE",
            details="Mauvais mot de passe enquêteur"
        )
        return

    enregistrer_action(
        acteur="ENQUETEUR",
        action="CONNEXION_REUSSIE",
        details="Enquêteur authentifié"
    )

    print("\n  ✅ Authentifié.")
    print("\n  [1] Lister les signalements")
    print("  [2] Consulter un signalement")
    print("  [3] Mettre à jour le statut d'un dossier")
    print("  [0] Retour")

    choix = input("\n  Votre choix : ").strip()

    if choix == "1":
        signalements = lister_signalements()
        if not signalements:
            print("\n  Aucun signalement trouvé.")
        else:
            print(f"\n  {len(signalements)} signalement(s) :\n")
            for i, s in enumerate(signalements, 1):
                print(f"  [{i}] Token   : {s['token']}")
                print(f"       Catégorie : {s['categorie']}")
                print(f"       Date      : {s['horodatage']}")
                print(f"       Statut    : {s['statut']}")
                print()

    elif choix == "2":
        token = input("\n  Token complet du dossier : ").strip()
        if token:
            signalement = consulter_signalement(token)
            if signalement:
                print("\n" + "-"*55)
                print(f"  📁 Dossier #{token[:8]}...")
                print(f"  Catégorie  : {signalement['categorie']}")
                print(f"  Date       : {signalement['horodatage']}")
                print(f"  Statut     : {signalement['statut']}")
                print(f"  Contenu    : {signalement['contenu']}")
                print("-"*55)

    elif choix == "3":
        token = input("\n  Token du dossier : ").strip()
        print("  Nouveaux statuts disponibles :")
        print("  [1] en_cours")
        print("  [2] cloture")
        print("  [3] escalade")
        statuts = {"1": "en_cours", "2": "cloture", "3": "escalade"}
        choix_statut = input("  Votre choix : ").strip()
        nouveau_statut = statuts.get(choix_statut)
        if nouveau_statut and token:
            mettre_a_jour_statut(token, nouveau_statut)

def menu_auditeur():
    print("\n" + "-"*55)
    print("  MODE : AUDITEUR")
    print("-"*55)
    print("  Authentification requise.")

    mot_de_passe = input("  Mot de passe auditeur : ").strip()

    if mot_de_passe != "auditeur2026":
        print("  ❌ Mot de passe incorrect.")
        enregistrer_action(
            acteur="INCONNU",
            action="TENTATIVE_CONNEXION_ECHOUEE",
            details="Mauvais mot de passe auditeur"
        )
        return

    enregistrer_action(
        acteur="AUDITEUR",
        action="CONNEXION_REUSSIE",
        details="Auditeur authentifié"
    )

    print("\n  ✅ Authentifié.")
    print("\n  [1] Afficher le journal d'audit")
    print("  [2] Vérifier l'intégrité du journal")
    print("  [3] Exporter le journal")
    print("  [0] Retour")

    choix = input("\n  Votre choix : ").strip()

    if choix == "1":
        afficher_journal()
    elif choix == "2":
        verifier_journal()
    elif choix == "3":
        exporter_journal()

def main():
    print("\n  Initialisation de ZeroTrace...")
    generer_cles()
    print("  ✅ Système prêt.\n")

    while True:
        afficher_menu_principal()
        choix = input("  Votre choix : ").strip()

        if choix == "1":
            menu_lanceur()
        elif choix == "2":
            menu_enqueteur()
        elif choix == "3":
            menu_auditeur()
        elif choix == "0":
            print("\n  Au revoir.\n")
            sys.exit(0)
        else:
            print("  ❌ Choix invalide.")

if __name__ == "__main__":
    main()