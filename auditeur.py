import json
from audit import charger_journal, verifier_integrite_journal
from crypto_utils import charger_secret_hmac

def afficher_journal():
    """Affiche toutes les entrées du journal d'audit de façon lisible."""
    entrees = charger_journal()

    if not entrees:
        print("\n[AUDITEUR] Journal vide — aucune action enregistrée.")
        return

    print("\n" + "="*65)
    print("         JOURNAL D'AUDIT ZEROTRACE")
    print("="*65)
    print(f"  Total entrées : {len(entrees)}")
    print("="*65 + "\n")

    for entree in entrees:
        print(f"  📋 Entrée #{entree['id']}")
        print(f"  🕐 Horodatage  : {entree['horodatage']}")
        print(f"  👤 Acteur      : {entree['acteur']}")
        print(f"  ⚡ Action      : {entree['action']}")
        print(f"  📝 Détails     : {entree['details']}")
        print(f"  🔗 Hash préc.  : {entree['hash_precedent'][:32]}...")
        print(f"  🔐 Signature   : {entree['signature'][:32]}...")
        print("-"*65)

def verifier_journal():
    """Lance la vérification complète de l'intégrité du journal."""
    print("\n" + "="*65)
    print("     VÉRIFICATION D'INTÉGRITÉ DU JOURNAL")
    print("="*65)
    verifier_integrite_journal()
    print("="*65 + "\n")

def exporter_journal(fichier_export: str = "export_audit.json"):
    """Exporte le journal dans un fichier séparé pour vérification externe."""
    entrees = charger_journal()

    with open(fichier_export, "w") as f:
        json.dump({
            "systeme": "ZeroTrace",
            "total_entrees": len(entrees),
            "entrees": entrees
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[AUDITEUR] ✅ Journal exporté → {fichier_export}")
    print(f"[AUDITEUR] {len(entrees)} entrée(s) exportée(s).\n")