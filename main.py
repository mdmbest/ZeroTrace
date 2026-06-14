import sys
from crypto_utils import generer_cles
from auth import initialiser_users, authentifier
from admin import menu_admin, get_dossiers_enqueteur
from signalement import (
    soumettre_signalement,
    consulter_signalement,
    lister_signalements,
    mettre_a_jour_statut
)
from canal import menu_canal_lanceur, menu_canal_enqueteur
from auditeur import afficher_journal, verifier_journal, exporter_journal
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
    print("  [4] ⚙️   Administrateur  — Gérer les comptes")
    print("  [0] 🚪  Quitter")
    print("="*55)

def menu_lanceur():
    print("\n" + "-"*55)
    print("  MODE : LANCEUR D'ALERTE")
    print("-"*55)
    print("  [1] Soumettre un nouveau signalement")
    print("  [2] Suivre mon dossier (via token)")
    print("  [3] Canal de communication anonyme")
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
        cat = input("\n  Choisissez une catégorie : ").strip()
        categories = {
            "1": "Corruption / Détournement de fonds",
            "2": "Fraude académique",
            "3": "Abus de pouvoir",
            "4": "Trafic de substances illicites",
            "5": "Autre"
        }
        categorie = categories.get(cat, "Autre")
        print("\n  Décrivez les faits :")
        contenu = input("  > ").strip()
        if contenu:
            token = soumettre_signalement(categorie, contenu)
            print(f"\n  ⚠️  Conservez votre token !")
        else:
            print("  ❌ Contenu vide — annulé.")

    elif choix == "2":
        token = input("\n  Entrez votre token : ").strip()
        if token:
            signalement = consulter_signalement(token)
            if signalement:
                print("\n" + "-"*55)
                print(f"  Catégorie : {signalement['categorie']}")
                print(f"  Date      : {signalement['horodatage']}")
                print(f"  Statut    : {signalement['statut']}")
                print(f"  Contenu   : {signalement['contenu']}")
                print("-"*55)

    elif choix == "3":
        token = input("\n  Entrez votre token : ").strip()
        if token:
            menu_canal_lanceur(token)

def menu_enqueteur():
    print("\n" + "-"*55)
    print("  MODE : ENQUÊTEUR")
    print("  Authentification requise (bcrypt + TOTP)")
    print("-"*55)

    username = input("  Nom d'utilisateur : ").strip()
    mot_de_passe = input("  Mot de passe : ").strip()
    code_totp = input("  Code TOTP (Google Authenticator) : ").strip()

    user, erreur = authentifier(username, mot_de_passe, code_totp)
    if erreur:
        print(f"\n  ❌ {erreur}")
        return

    if user["role"] not in ["enqueteur", "admin"]:
        print("  ❌ Accès non autorisé.")
        return

    print(f"\n  ✅ Authentifié. Niveau {user['niveau']}.")

    # Dossiers affectés à cet enquêteur (DAC)
    dossiers_autorises = get_dossiers_enqueteur(username)

    while True:
        print("\n  [1] Mes dossiers affectés")
        print("  [2] Consulter un dossier")
        print("  [3] Mettre à jour le statut")
        print("  [4] Canal de communication")
        print("  [0] Retour")

        choix = input("\n  Votre choix : ").strip()

        if choix == "1":
            if not dossiers_autorises:
                print("\n  Aucun dossier affecté.")
            else:
                print(f"\n  {len(dossiers_autorises)} dossier(s) affecté(s) :\n")
                for token in dossiers_autorises:
                    sig = consulter_signalement(token)
                    if sig:
                        print(f"  Token   : {token[:8]}...")
                        print(f"  Cat     : {sig['categorie']}")
                        print(f"  Statut  : {sig['statut']}\n")

        elif choix == "2":
            token = input("\n  Token du dossier : ").strip()
            if token not in dossiers_autorises:
                print("  ❌ Accès refusé — dossier non affecté.")
                enregistrer_action(username, "ACCES_REFUSE",
                                   f"Token: {token[:8]}...")
                continue
            sig = consulter_signalement(token)
            if sig:
                print("\n" + "-"*55)
                print(f"  Catégorie : {sig['categorie']}")
                print(f"  Date      : {sig['horodatage']}")
                print(f"  Statut    : {sig['statut']}")
                print(f"  Contenu   : {sig['contenu']}")
                print("-"*55)

        elif choix == "3":
            token = input("\n  Token du dossier : ").strip()
            if token not in dossiers_autorises:
                print("  ❌ Accès refusé.")
                continue
            print("  [1] en_cours  [2] cloture  [3] escalade")
            s = input("  Statut : ").strip()
            statuts = {"1":"en_cours","2":"cloture","3":"escalade"}
            if s in statuts:
                mettre_a_jour_statut(token, statuts[s])

        elif choix == "4":
            token = input("\n  Token du dossier : ").strip()
            if token not in dossiers_autorises:
                print("  ❌ Accès refusé.")
                continue
            menu_canal_enqueteur(token, username)

        elif choix == "0":
            break

def menu_auditeur():
    print("\n" + "-"*55)
    print("  MODE : AUDITEUR")
    print("  Authentification requise (bcrypt + TOTP)")
    print("-"*55)

    username = input("  Nom d'utilisateur : ").strip()
    mot_de_passe = input("  Mot de passe : ").strip()
    code_totp = input("  Code TOTP : ").strip()

    user, erreur = authentifier(username, mot_de_passe, code_totp)
    if erreur:
        print(f"\n  ❌ {erreur}")
        return

    if user["role"] != "auditeur" and user["role"] != "admin":
        print("  ❌ Accès non autorisé.")
        return

    print("\n  ✅ Authentifié.")
    print("\n  [1] Afficher le journal")
    print("  [2] Vérifier l'intégrité")
    print("  [3] Exporter le journal")
    choix = input("\n  Votre choix : ").strip()

    if choix == "1":
        afficher_journal()
    elif choix == "2":
        verifier_journal()
    elif choix == "3":
        exporter_journal()

def menu_administrateur():
    print("\n" + "-"*55)
    print("  MODE : ADMINISTRATEUR")
    print("  Authentification requise (bcrypt + TOTP)")
    print("-"*55)

    username = input("  Nom d'utilisateur : ").strip()
    mot_de_passe = input("  Mot de passe : ").strip()
    code_totp = input("  Code TOTP : ").strip()

    user, erreur = authentifier(username, mot_de_passe, code_totp)
    if erreur:
        print(f"\n  ❌ {erreur}")
        return

    if user["role"] != "admin":
        print("  ❌ Accès non autorisé.")
        return

    print("\n  ✅ Authentifié en tant qu'administrateur.")
    menu_admin(user)

def main():
    print("\n  Initialisation de ZeroTrace...")
    generer_cles()
    initialiser_users()
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
        elif choix == "4":
            menu_administrateur()
        elif choix == "0":
            print("\n  Au revoir.\n")
            sys.exit(0)
        else:
            print("  ❌ Choix invalide.")

if __name__ == "__main__":
    main()