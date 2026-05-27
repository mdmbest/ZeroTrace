import os
import json
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEYS_DIR = "keys"
PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "public_key.pem")
HMAC_SECRET_FILE = os.path.join(KEYS_DIR, "hmac_secret.key")

def generer_cles():
    """Génère une paire de clés RSA et un secret HMAC si inexistants."""
    os.makedirs(KEYS_DIR, exist_ok=True)

    if not os.path.exists(PRIVATE_KEY_FILE):
        cle_privee = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(cle_privee.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(cle_privee.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("[CRYPTO] Paire de clés RSA générée.")

    if not os.path.exists(HMAC_SECRET_FILE):
        secret = os.urandom(32)
        with open(HMAC_SECRET_FILE, "wb") as f:
            f.write(secret)
        print("[CRYPTO] Secret HMAC généré.")

def charger_cle_publique():
    with open(PUBLIC_KEY_FILE, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def charger_cle_privee():
    with open(PRIVATE_KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def charger_secret_hmac():
    with open(HMAC_SECRET_FILE, "rb") as f:
        return f.read()

def chiffrer_message(message: str) -> dict:
    """Chiffre un message avec AES-GCM, la clé AES étant chiffrée par RSA."""
    cle_publique = charger_cle_publique()

    # Générer une clé AES aléatoire
    cle_aes = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    aesgcm = AESGCM(cle_aes)

    # Chiffrer le message
    message_chiffre = aesgcm.encrypt(nonce, message.encode(), None)

    # Chiffrer la clé AES avec RSA
    cle_aes_chiffree = cle_publique.encrypt(
        cle_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return {
        "cle_aes_chiffree": cle_aes_chiffree.hex(),
        "nonce": nonce.hex(),
        "message_chiffre": message_chiffre.hex()
    }

def dechiffrer_message(donnees: dict) -> str:
    """Déchiffre un message chiffré."""
    cle_privee = charger_cle_privee()

    cle_aes = cle_privee.decrypt(
        bytes.fromhex(donnees["cle_aes_chiffree"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aesgcm = AESGCM(cle_aes)
    message = aesgcm.decrypt(
        bytes.fromhex(donnees["nonce"]),
        bytes.fromhex(donnees["message_chiffre"]),
        None
    )
    return message.decode()

def calculer_hmac(donnees: str) -> str:
    """Calcule le HMAC-SHA256 d'une chaîne."""
    secret = charger_secret_hmac()
    h = hmac.new(secret, donnees.encode(), hashlib.sha256)
    return h.hexdigest()

def verifier_hmac(donnees: str, signature: str) -> bool:
    """Vérifie le HMAC d'une chaîne."""
    signature_calculee = calculer_hmac(donnees)
    return hmac.compare_digest(signature_calculee, signature)