import os
import json
from datetime import datetime
from crypto_utils import chiffrer_message, dechiffrer_message
from audit import enregistrer_action

CANAL_FILE = "data/canal_messages.json"

def initialiser_canal():
    """Crée le fichier de messages s'il n'existe pas."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CANAL_FILE):
        with open(CANAL_FILE, "w") as f:
            json.dump({}, f, indent=2)

def charger_messages():
    initialiser_canal()
    with open(CANAL_FILE, "r") as f:
        return json.load(f)

def sauvegarder_messages(messages):
    with open(CANAL_FILE, "w") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def envoyer_message_lanceur(token, contenu):
    """
    Le lanceur envoie un message anonyme à l'enquêteur.
    Le contenu est chiffré avant stockage.
    """
    messages = charger_messages()
    if token not in messages:
        messages[token] = []

    message_chiffre = chiffrer_message(contenu)

    message = {
        "id": len(messages[token]) + 1,
        "expediteur": "ANONYME",
        "horodatage": datetime.now().isoformat(),
        "contenu_chiffre": message_chiffre
    }
    messages[token].append(message)
    sauvegarder_messages(messages)

    enregistrer_action(
        "ANONYME",
        "MESSAGE_ENVOYE",
        f"Token: {token[:8]}... | Message #{message['id']}"
    )
    print("\n[CANAL] ✅ Message envoyé avec succès.")

def envoyer_message_enqueteur(token, username, contenu):
    """
    L'enquêteur envoie un message vers le lanceur anonyme.
    """
    messages = charger_messages()
    if token not in messages:
        messages[token] = []

    message_chiffre = chiffrer_message(contenu)

    message = {
        "id": len(messages[token]) + 1,
        "expediteur": "ENQUETEUR",
        "horodatage": datetime.now().isoformat(),
        "contenu_chiffre": message_chiffre
    }
    messages[token].append(message)
    sauvegarder_messages(messages)

    enregistrer_action(
        username,
        "MESSAGE_ENVOYE",
        f"Token: {token[:8]}... | Message #{message['id']}"
    )
    print("\n[CANAL] ✅ Message envoyé avec succès.")

def lire_messages(token):
    """
    Lit et déchiffre tous les messages d'un dossier.
    Accessible au lanceur (via token) et à l'enquêteur.
    """
    messages = charger_messages()
    if token not in messages or not messages[token]:
        print("\n[CANAL] Aucun message pour ce dossier.")
        return []

    msgs_dechiffres = []
    for msg in messages[token]:
        try:
            contenu = dechiffrer_message(msg["contenu_chiffre"])
            msgs_dechiffres.append({
                "id": msg["id"],
                "expediteur": msg["expediteur"],
                "horodatage": msg["horodatage"],
                "contenu": contenu
            })
        except Exception:
            msgs_dechiffres.append({
                "id": msg["id"],
                "expediteur": msg["expediteur"],
                "horodatage": msg["horodatage"],
                "contenu": "[Erreur de déchiffrement]"
            })
    return msgs_dechiffres

def afficher_messages(token):
    """Affiche les messages déchiffrés d'un dossier."""
    msgs = lire_messages(token)
    if not msgs:
        return

    print("\n" + "="*55)
    print(f"  CANAL ANONYME — Dossier #{token[:8]}...")
    print("="*55)
    for msg in msgs:
        expediteur = "👤 Lanceur (anonyme)" if msg["expediteur"] == "ANONYME" \
                     else "🔍 Enquêteur"
        print(f"\n  [{msg['id']}] {expediteur}")
        print(f"  Heure : {msg['horodatage']}")
        print(f"  Message : {msg['contenu']}")
        print("  " + "-"*50)

def menu_canal_lanceur(token):
    """Menu du canal pour le lanceur d'alerte."""
    while True:
        print("\n" + "-"*55)
        print("  CANAL DE COMMUNICATION ANONYME")
        print("-"*55)
        print("  [1] Envoyer un message à l'enquêteur")
        print("  [2] Lire les messages")
        print("  [0] Retour")
        print("-"*55)

        choix = input("  Votre choix : ").strip()

        if choix == "1":
            contenu = input("\n  Votre message : ").strip()
            if contenu:
                envoyer_message_lanceur(token, contenu)
            else:
                print("  Message vide — annulé.")

        elif choix == "2":
            afficher_messages(token)

        elif choix == "0":
            break

def menu_canal_enqueteur(token, username):
    """Menu du canal pour l'enquêteur."""
    while True:
        print("\n" + "-"*55)
        print("  CANAL DE COMMUNICATION ANONYME")
        print("-"*55)
        print("  [1] Envoyer un message au lanceur")
        print("  [2] Lire les messages")
        print("  [0] Retour")
        print("-"*55)

        choix = input("  Votre choix : ").strip()

        if choix == "1":
            contenu = input("\n  Votre message : ").strip()
            if contenu:
                envoyer_message_enqueteur(token, username, contenu)
            else:
                print("  Message vide — annulé.")

        elif choix == "2":
            afficher_messages(token)

        elif choix == "0":
            break