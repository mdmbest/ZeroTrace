import os
import json
import bcrypt
import pyotp
import qrcode
from datetime import datetime
from audit import enregistrer_action

USERS_FILE = "keys/users.json"

def initialiser_users():
    """Crée le fichier users.json s'il n'existe pas."""
    os.makedirs("keys", exist_ok=True)
    if not os.path.exists(USERS_FILE):
        # Créer un compte admin par défaut
        admin = {
            "admin": {
                "role": "admin",
                "mot_de_passe": bcrypt.hashpw(
                    "admin2026".encode(), bcrypt.gensalt()
                ).decode(),
                "totp_secret": pyotp.random_base32(),
                "niveau": 3,
                "actif": True,
                "date_creation": datetime.now().isoformat()
            }
        }
        with open(USERS_FILE, "w") as f:
            json.dump(admin, f, indent=2, ensure_ascii=False)
        print("[AUTH] Compte admin créé (mot de passe : admin2026)")

def charger_users():
    initialiser_users()
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def sauvegarder_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def creer_compte(username, mot_de_passe, role, niveau=1):
    """Crée un nouveau compte utilisateur avec bcrypt + TOTP."""
    users = charger_users()
    if username in users:
        print(f"[AUTH] Utilisateur '{username}' existe déjà.")
        return False

    totp_secret = pyotp.random_base32()
    users[username] = {
        "role": role,
        "mot_de_passe": bcrypt.hashpw(
            mot_de_passe.encode(), bcrypt.gensalt()
        ).decode(),
        "totp_secret": totp_secret,
        "niveau": niveau,
        "actif": True,
        "date_creation": datetime.now().isoformat()
    }
    sauvegarder_users(users)
    enregistrer_action("ADMIN", "CREATION_COMPTE",
                       f"Utilisateur: {username} | Rôle: {role} | Niveau: {niveau}")
    print(f"\n[AUTH] Compte '{username}' créé avec succès.")
    print(f"[AUTH] Secret TOTP : {totp_secret}")
    print(f"[AUTH] Pour configurer Google Authenticator, scannez le QR code.")

    # Générer QR code
    totp = pyotp.TOTP(totp_secret)
    uri = totp.provisioning_uri(name=username, issuer_name="ZeroTrace")
    qr = qrcode.make(uri)
    qr_path = f"keys/qr_{username}.png"
    qr.save(qr_path)
    print(f"[AUTH] QR code sauvegardé : {qr_path}")
    return True

def authentifier(username, mot_de_passe, code_totp):
    """Authentifie un utilisateur avec bcrypt + TOTP."""
    users = charger_users()

    if username not in users:
        enregistrer_action("INCONNU", "TENTATIVE_CONNEXION_ECHOUEE",
                           f"Utilisateur inexistant: {username}")
        return None, "Utilisateur introuvable."

    user = users[username]

    if not user.get("actif", False):
        enregistrer_action(username, "TENTATIVE_CONNEXION_ECHOUEE",
                           "Compte désactivé")
        return None, "Compte désactivé."

    # Vérifier mot de passe bcrypt
    if not bcrypt.checkpw(mot_de_passe.encode(),
                          user["mot_de_passe"].encode()):
        enregistrer_action(username, "TENTATIVE_CONNEXION_ECHOUEE",
                           "Mot de passe incorrect")
        return None, "Mot de passe incorrect."

    # Vérifier TOTP
    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(code_totp):
        enregistrer_action(username, "TENTATIVE_CONNEXION_ECHOUEE",
                           "Code TOTP invalide")
        return None, "Code TOTP invalide."

    enregistrer_action(username, "CONNEXION_REUSSIE",
                       f"Rôle: {user['role']} | Niveau: {user['niveau']}")
    return user, None

def revoquer_compte(username):
    """Désactive un compte utilisateur."""
    users = charger_users()
    if username not in users:
        print(f"[AUTH] Utilisateur '{username}' introuvable.")
        return False
    users[username]["actif"] = False
    sauvegarder_users(users)
    enregistrer_action("ADMIN", "REVOCATION_COMPTE",
                       f"Utilisateur désactivé: {username}")
    print(f"[AUTH] Compte '{username}' désactivé.")
    return True

def lister_comptes():
    """Liste tous les comptes."""
    users = charger_users()
    return [
        {
            "username": u,
            "role": d["role"],
            "niveau": d["niveau"],
            "actif": d["actif"],
            "date_creation": d["date_creation"]
        }
        for u, d in users.items()
    ]