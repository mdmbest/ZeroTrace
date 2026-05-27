import os
import json
import uuid
import hashlib
from datetime import datetime
from crypto_utils import chiffrer_message, dechiffrer_message
from audit import enregistrer_action

DATA_DIR = "data"

def initialiser_stockage():
    """Crée le dossier de stockage s'il n'existe pas."""
    os.makedirs(DATA_DIR, exist_ok=True)

def soumettre_signalement(categorie: str, contenu: str) -> str:
    """
    Soumet un signalement anonyme.
    Le contenu est chiffré avant stockage.
    Retourne le token de suivi anonyme.
    """
    initialiser_stockage()

    # Générer un token anonyme unique
    token = str(uuid.uuid4())

    # Chiffrer le contenu
    contenu_chiffre = chiffrer_message(contenu)

    # Calculer le hash du contenu original (intégrité)
    hash_contenu = hashlib.sha256(contenu.encode()).hexdigest()

    # Construire le signalement
    signalement = {
        "token": token,
        "categorie": categorie,
        "horodatage": datetime.now().isoformat(),
        "contenu_chiffre": contenu_chiffre,
        "hash_contenu": hash_contenu,
        "statut": "recu"
    }

    # Sauvegarder le signalement chiffré
    fichier = os.path.join(DATA_DIR, f"{token}.json")
    with open(fichier, "w") as f:
        json.dump(signalement, f, indent=2, ensure_ascii=False)

    # Enregistrer dans le journal d'audit
    enregistrer_action(
        acteur="ANONYME",
        action="SOUMISSION_SIGNALEMENT",
        details=f"Catégorie: {categorie} | Hash: {hash_contenu[:16]}..."
    )

    print(f"\n[SIGNALEMENT] ✅ Signalement soumis avec succès.")
    print(f"[SIGNALEMENT] 🔑 Votre token de suivi (conservez-le) :")
    print(f"              {token}\n")

    return token

def consulter_signalement(token: str) -> dict | None:
    """
    Consulte un signalement via son token.
    Déchiffre le contenu pour l'enquêteur.
    """
    fichier = os.path.join(DATA_DIR, f"{token}.json")

    if not os.path.exists(fichier):
        print("[SIGNALEMENT] ❌ Token invalide ou signalement introuvable.")
        return None

    with open(fichier, "r") as f:
        signalement = json.load(f)

    # Déchiffrer le contenu
    contenu_dechiffre = dechiffrer_message(signalement["contenu_chiffre"])

    # Enregistrer la consultation dans le journal
    enregistrer_action(
        acteur="ENQUETEUR",
        action="CONSULTATION_SIGNALEMENT",
        details=f"Token: {token[:8]}... | Statut: {signalement['statut']}"
    )

    return {
        "token": token,
        "categorie": signalement["categorie"],
        "horodatage": signalement["horodatage"],
        "contenu": contenu_dechiffre,
        "statut": signalement["statut"]
    }

def lister_signalements() -> list:
    """Liste tous les signalements disponibles (tokens uniquement)."""
    initialiser_stockage()
    fichiers = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    signalements = []
    for fichier in fichiers:
        with open(os.path.join(DATA_DIR, fichier), "r") as f:
            s = json.load(f)
            signalements.append({
                "token": s["token"][:8] + "...",
                "token_complet": s["token"],
                "categorie": s["categorie"],
                "horodatage": s["horodatage"],
                "statut": s["statut"]
            })

    enregistrer_action(
        acteur="ENQUETEUR",
        action="LISTE_SIGNALEMENTS",
        details=f"{len(signalements)} signalement(s) trouvé(s)"
    )

    return signalements

def mettre_a_jour_statut(token: str, nouveau_statut: str):
    """Met à jour le statut d'un dossier."""
    fichier = os.path.join(DATA_DIR, f"{token}.json")

    if not os.path.exists(fichier):
        print("[SIGNALEMENT] ❌ Token invalide.")
        return False

    with open(fichier, "r") as f:
        signalement = json.load(f)

    ancien_statut = signalement["statut"]
    signalement["statut"] = nouveau_statut

    with open(fichier, "w") as f:
        json.dump(signalement, f, indent=2, ensure_ascii=False)

    enregistrer_action(
        acteur="ENQUETEUR",
        action="MISE_A_JOUR_STATUT",
        details=f"Token: {token[:8]}... | {ancien_statut} → {nouveau_statut}"
    )

    print(f"[SIGNALEMENT] ✅ Statut mis à jour : {ancien_statut} → {nouveau_statut}")
    return True