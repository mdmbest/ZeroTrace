import os
import json
import datetime
from crypto_utils import calculer_hmac, verifier_hmac

LOGS_DIR = "logs"
JOURNAL_FILE = os.path.join(LOGS_DIR, "journal_audit.json")

def initialiser_journal():
    """Crée le journal d'audit s'il n'existe pas."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    if not os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "w") as f:
            json.dump([], f)

def charger_journal() -> list:
    """Charge toutes les entrées du journal."""
    if not os.path.exists(JOURNAL_FILE):
        return []
    with open(JOURNAL_FILE, "r") as f:
        return json.load(f)

def sauvegarder_journal(entrees: list):
    """Sauvegarde le journal sur disque."""
    with open(JOURNAL_FILE, "w") as f:
        json.dump(entrees, f, indent=2, ensure_ascii=False)

def enregistrer_action(acteur: str, action: str, details: str = ""):
    """
    Enregistre une action dans le journal d'audit.
    Chaque entrée est signée HMAC et enchaînée à la précédente.
    """
    initialiser_journal()
    entrees = charger_journal()

    # Hash de l'entrée précédente (chaînage)
    if entrees:
        hash_precedent = calculer_hmac(json.dumps(entrees[-1], ensure_ascii=False))
    else:
        hash_precedent = "GENESIS"

    # Construire l'entrée
    entree = {
        "id": len(entrees) + 1,
        "horodatage": datetime.datetime.now().isoformat(),
        "acteur": acteur,
        "action": action,
        "details": details,
        "hash_precedent": hash_precedent
    }

    # Signer l'entrée avec HMAC
    entree_str = json.dumps(entree, ensure_ascii=False)
    entree["signature"] = calculer_hmac(entree_str)

    entrees.append(entree)
    sauvegarder_journal(entrees)

    print(f"[AUDIT] Action enregistrée : {action} par {acteur}")

def verifier_integrite_journal() -> bool:
    """
    Vérifie l'intégrité de toutes les entrées du journal.
    Détecte toute modification ou suppression.
    """
    entrees = charger_journal()

    if not entrees:
        print("[AUDIT] Journal vide.")
        return True

    print(f"\n[AUDIT] Vérification de {len(entrees)} entrée(s)...\n")
    integre = True

    for i, entree in enumerate(entrees):
        # Extraire la signature stockée
        signature_stockee = entree.pop("signature", None)

        # Recalculer la signature
        entree_str = json.dumps(entree, ensure_ascii=False)
        signature_calculee = calculer_hmac(entree_str)

        # Vérifier le chaînage
        if i > 0:
            hash_precedent_attendu = calculer_hmac(
                json.dumps(entrees[i-1], ensure_ascii=False)
            )
            chainageOK = (entree["hash_precedent"] == hash_precedent_attendu)
        else:
            chainageOK = (entree["hash_precedent"] == "GENESIS")

        # Vérifier la signature
        signatureOK = (signature_stockee == signature_calculee)

        # Remettre la signature
        entree["signature"] = signature_stockee

        statut = "✅ OK" if (signatureOK and chainageOK) else "❌ ALTÉRÉE"
        print(f"  Entrée #{entree['id']} | {entree['horodatage']} | "
              f"{entree['acteur']} | {entree['action']} | {statut}")

        if not (signatureOK and chainageOK):
            integre = False
            if not signatureOK:
                print(f"    ⚠️  Signature invalide !")
            if not chainageOK:
                print(f"    ⚠️  Chaînage rompu !")

    print()
    if integre:
        print("[AUDIT] ✅ Journal intègre — aucune modification détectée.")
    else:
        print("[AUDIT] ❌ Journal compromis — des entrées ont été modifiées !")

    return integre