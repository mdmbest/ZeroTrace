import os
import json
from auth import (
    creer_compte, revoquer_compte,
    lister_comptes, charger_users, sauvegarder_users
)
from audit import enregistrer_action
from signalement import lister_signalements

AFFECTATIONS_FILE = "data/affectations.json"

def initialiser_affectations():
    """Crée le fichier d'affectations s'il n'existe pas."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(AFFECTATIONS_FILE):
        with open(AFFECTATIONS_FILE, "w") as f:
            json.dump({}, f, indent=2)

def charger_affectations():
    initialiser_affectations()
    with open(AFFECTATIONS_FILE, "r") as f:
        return json.load(f)

def sauvegarder_affectations(affectations):
    with open(AFFECTATIONS_FILE, "w") as f:
        json.dump(affectations, f, indent=2, ensure_ascii=False)

def affecter_dossier(token, username, niveau_requis=1):
    """Affecte un dossier à un enquêteur avec niveau de classification."""
    users = charger_users()
    if username not in users:
        print(f"[ADMIN] Enquêteur '{username}' introuvable.")
        return False

    if users[username]["role"] != "enqueteur":
        print(f"[ADMIN] '{username}' n'est pas un enquêteur.")
        return False

    if users[username]["niveau"] < niveau_requis:
        print(f"[ADMIN] Niveau insuffisant pour ce dossier.")
        return False

    affectations = charger_affectations()
    affectations[token] = {
        "enqueteur": username,
        "niveau_requis": niveau_requis,
        "date_affectation": __import__('datetime').datetime.now().isoformat()
    }
    sauvegarder_affectations(affectations)
    enregistrer_action(
        "ADMIN", "AFFECTATION_DOSSIER",
        f"Token: {token[:8]}... | Enquêteur: {username} | Niveau: {niveau_requis}"
    )
    print(f"\n[ADMIN] Dossier affecté à '{username}' avec succès.")
    return True

def get_dossiers_enqueteur(username):
    """Retourne les tokens des dossiers affectés à un enquêteur."""
    affectations = charger_affectations()
    return [
        token for token, info in affectations.items()
        if info["enqueteur"] == username
    ]

def menu_admin(user_connecte):
    """Menu principal de l'administrateur."""
    while True:
        print("\n" + "-"*55)
        print("  MODE : ADMINISTRATEUR")
        print(f"  Connecté : {user_connecte['role']} — Niveau {user_connecte['niveau']}")
        print("-"*55)
        print("  [1] Créer un compte enquêteur")
        print("  [2] Lister tous les comptes")
        print("  [3] Affecter un dossier à un enquêteur")
        print("  [4] Lister les dossiers non affectés")
        print("  [5] Révoquer un compte")
        print("  [0] Retour")
        print("-"*55)

        choix = input("  Votre choix : ").strip()

        if choix == "1":
            print("\n  Création d'un compte enquêteur")
            username = input("  Nom d'utilisateur : ").strip()
            mot_de_passe = input("  Mot de passe : ").strip()
            print("  Niveau d'habilitation :")
            print("  [1] Niveau 1 — Dossiers basiques")
            print("  [2] Niveau 2 — Dossiers sensibles")
            print("  [3] Niveau 3 — Dossiers critiques")
            niv = input("  Choisissez : ").strip()
            niveau = int(niv) if niv in ["1","2","3"] else 1
            creer_compte(username, mot_de_passe, "enqueteur", niveau)

        elif choix == "2":
            comptes = lister_comptes()
            print(f"\n  {len(comptes)} compte(s) :\n")
            for c in comptes:
                statut = "Actif" if c["actif"] else "Désactivé"
                print(f"  - {c['username']} | {c['role']} | "
                      f"Niveau {c['niveau']} | {statut}")

        elif choix == "3":
            signalements = lister_signalements()
            if not signalements:
                print("\n  Aucun signalement disponible.")
                continue
            print(f"\n  {len(signalements)} signalement(s) :\n")
            for s in signalements:
                print(f"  Token : {s['token']} | "
                      f"Cat : {s['categorie']} | "
                      f"Statut : {s['statut']}")

            token = input("\n  Token complet à affecter : ").strip()
            username = input("  Nom de l'enquêteur : ").strip()
            print("  Niveau de classification du dossier (1/2/3) : ")
            niv = input("  : ").strip()
            niveau = int(niv) if niv in ["1","2","3"] else 1
            affecter_dossier(token, username, niveau)

        elif choix == "4":
            affectations = charger_affectations()
            signalements = lister_signalements()
            non_affectes = [
                s for s in signalements
                if s["token_complet"] not in affectations
            ]
            if not non_affectes:
                print("\n  Tous les dossiers sont affectés.")
            else:
                print(f"\n  {len(non_affectes)} dossier(s) non affecté(s) :\n")
                for s in non_affectes:
                    print(f"  - {s['token']} | {s['categorie']} | {s['statut']}")

        elif choix == "5":
            username = input("  Nom d'utilisateur à révoquer : ").strip()
            revoquer_compte(username)

        elif choix == "0":
            break