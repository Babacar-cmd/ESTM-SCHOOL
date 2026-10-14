
import fitz
from datetime import datetime, timedelta
import json, re

def extract_text_from_pdf(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if len(text.strip()) < 50:
            return {"success": False, "text": "", "warning": "PDF scanné ou image – extraction OCR non disponible. Veuillez copier le texte manuellement."}
        return {"success": True, "text": text, "pages": len(doc) if 'doc' in locals() else 0}
    except Exception as e:
        return {"success": False, "text": "", "warning": f"Erreur lecture PDF: {str(e)}"}

def extract_text_from_txt(file_bytes):
    try:
        for enc in ["utf-8","latin-1","cp1252"]:
            try:
                return {"success": True, "text": file_bytes.decode(enc)}
            except:
                continue
        return {"success": False, "text": "", "warning": "Encodage non reconnu"}
    except Exception as e:
        return {"success": False, "text": "", "warning": str(e)}

def generate_fiche_auto(contenu, titre="Fiche"):
    # Heuristique locale sans IA externe
    lines = [l.strip() for l in contenu.split("\n") if l.strip()]
    notions = "\n".join([f"- {l[:120]}" for l in lines[:8]])
    definitions = "Définitions extraites des premières lignes:\n" + "\n".join([f"- {l}" for l in lines[:3]])
    points = "\n".join([f"• {l[:100]}" for l in lines[2:10]])
    return {
        "notions": notions or "Contenu à synthétiser manuellement",
        "definitions": definitions,
        "points_cles": points,
        "formules": "À compléter selon le cours",
        "exemples": "Exemple générique : voir contenu original",
        "erreurs": "Confusion fréquente : relire définitions",
        "resume": "\n".join(lines[:5])[:500] + "..."
    }

def calculate_quiz_score(answers, questions):
    correct = 0
    total = len(questions)
    details = []
    for q in questions:
        qid = q["id"]
        expected = json.loads(q["reponses_correctes"]) if isinstance(q["reponses_correctes"], str) else q["reponses_correctes"]
        given = answers.get(qid, [])
        if isinstance(given, str):
            given = [given]
        # compare sets
        if set(map(str,given)) == set(map(str,expected)):
            correct+=1
            details.append({"qid": qid, "ok": True})
        else:
            details.append({"qid": qid, "ok": False, "expected": expected, "given": given})
    pct = (correct/total*100) if total else 0
    score20 = round(correct/total*20,2) if total else 0
    return {"correct": correct, "total": total, "pct": pct, "score20": score20, "details": details}

def spaced_next_review(statut):
    now = datetime.now()
    if statut == "Maîtrisé":
        return (now + timedelta(days=7)).isoformat()
    if statut == "En cours d'acquisition":
        return (now + timedelta(days=2)).isoformat()
    return (now + timedelta(days=1)).isoformat()
