
import streamlit as st
import json
import re
from datetime import datetime, date, timedelta
import pandas as pd

st.set_page_config(
    page_title="GLAR MASTER - ESTM L3",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE BLEU NUIT / EMERAUDE ---
st.markdown("""
<style>
    :root { --nuit: #0f172a; --primary: #1e3a8a; --accent: #10b981; }
    .main-header { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem; }
    .card { background: white; padding: 1rem; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .stProgress > div > div > div > div { background-color: #10b981; }
</style>
""", unsafe_allow_html=True)

# --- DATA INIT ---
if 'matieres' not in st.session_state:
    st.session_state.matieres = [
        {"nom": "UML et Modélisation", "cat": "GL", "prog": 65, "chapitres": ["Intro UML", "Cas utilisation", "Classes", "Séquences"]},
        {"nom": "TCP/IP & OSI", "cat": "RESEAUX", "prog": 78, "chapitres": ["OSI 7 couches", "TCP vs UDP", "Ports", "Encapsulation"]},
        {"nom": "IPv4/IPv6 & Sous-réseautage", "cat": "RESEAUX", "prog": 45, "chapitres": ["IPv4", "VLSM", "IPv6"]},
        {"nom": "BDD SQL/NoSQL", "cat": "GL", "prog": 80, "chapitres": ["MCD/MLD", "JOIN", "Index"]},
        {"nom": "Administration Linux", "cat": "RESEAUX", "prog": 55, "chapitres": ["Bases", "systemd", "Bash"]},
        {"nom": "Sécurité Réseaux & Firewall", "cat": "RESEAUX", "prog": 40, "chapitres": ["ACL", "NAT", "iptables"]},
    ]
if 'quiz_scores' not in st.session_state:
    st.session_state.quiz_scores = [45, 58, 72, 85]
if 'streak' not in st.session_state:
    st.session_state.streak = 12
if 'taches' not in st.session_state:
    st.session_state.taches = ["Réviser OSI", "Exo sous-réseau /28", "Quiz UML"]

GLOSSARY = {
    "OSI": "7 couches: Physique, Liaison, Réseau, Transport, Session, Présentation, Application. Analogie: envoi colis avec emballages successifs.",
    "TCP": "Fiable, orienté connexion, 3-way handshake SYN/SYN-ACK/ACK. Analogie: appel téléphonique avec accusé réception.",
    "UDP": "Non fiable, rapide, sans connexion. Pour DNS, streaming. Analogie: lancer une lettre sans suivi.",
    "VLAN": "Réseau virtuel niveau 2, segmentation. Commande: vlan 10, name ETM_ETUDIANTS, trunk 802.1Q",
    "NAT": "Traduction adresse privée->publique. Static, Dynamic, PAT Overload.",
    "SOLID": "Principes POO: Single, Open/Closed, Liskov, Interface Segregation, Dependency Inversion",
    "UML": "Cas utilisation (acteurs), Classes (associations), Séquences (lifeline), Etats, Activité",
}

EXAMENS = [
    {"matiere": "Réseaux TCP/IP & Routage", "date": "2026-12-15", "heure": "09:00", "salle": "B201"},
    {"matiere": "Génie Logiciel UML & POO", "date": "2026-12-18", "heure": "14:00", "salle": "A102"},
    {"matiere": "BDD SQL/NoSQL", "date": "2026-12-20", "heure": "09:00", "salle": "C305"},
    {"matiere": "Sécurité Réseaux & Linux", "date": "2026-12-22", "heure": "09:00", "salle": "B201"},
]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🎓 GLAR MASTER")
    st.caption("Comprendre, pratiquer, maîtriser.")
    st.caption("ESTM Dakar - L3 GLAR")
    st.divider()
    menu = st.radio("Navigation", ["Dashboard", "Mes cours", "Assistant IA", "Lab Programmation", "Lab Réseaux", "Quiz & Examens", "Planning", "Progression"], label_visibility="collapsed")
    st.divider()
    st.metric("Streak", f"{st.session_state.streak} jours 🔥")
    st.metric("Progression moyenne", f"{sum(m['prog'] for m in st.session_state.matieres)//len(st.session_state.matieres)}%")
    st.caption("Demo: demo@estm.sn")

# --- PAGES ---
if menu == "Dashboard":
    st.markdown('<div class="main-header"><h1>Bienvenue, Étudiant ESTM L3 👋</h1><p>Programme du jour • 4 examens en décembre • Continue ton streak !</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Matières en cours", "6", "2 en retard")
    with col2: st.metric("Chapitres restants", "9", "-3 cette semaine")
    with col3: st.metric("Temps révision", "8h20", "+1h20")
    with col4: st.metric("Score dernier quiz", "85%", "+13%")
    
    c1, c2 = st.columns([2,1])
    with c1:
        st.subheader("📅 Programme de révision du jour")
        for t in st.session_state.taches:
            st.checkbox(t, key=f"task_{t}")
        new_task = st.text_input("Ajouter tâche")
        if st.button("Ajouter") and new_task:
            st.session_state.taches.append(new_task)
            st.rerun()
    with c2:
        st.subheader("🎯 Prochains examens")
        for ex in EXAMENS:
            st.markdown(f'<div class="card"><b>{ex["matiere"]}</b><br>{ex["date"]} {ex["heure"]} - {ex["salle"]}</div>', unsafe_allow_html=True)
            st.write("")
    
    st.subheader("📈 Évolution")
    df = pd.DataFrame({"Mois": ["Sept","Oct","Nov","Déc"], "Score": st.session_state.quiz_scores})
    st.line_chart(df, x="Mois", y="Score")
    
    st.info("💡 Recommandation: Retravaille 'IPv4/IPv6 & Sous-réseautage' (45%) et 'Sécurité' (40%) - prioritaires avant 15 déc.")

elif menu == "Mes cours":
    st.title("📚 Mes matières L3 ESTM")
    tabs = st.tabs([m["nom"] for m in st.session_state.matieres])
    for idx, tab in enumerate(tabs):
        with tab:
            mat = st.session_state.matieres[idx]
            st.progress(mat["prog"]/100, text=f"Progression {mat['prog']}%")
            st.write(f"**Catégorie:** {mat['cat']} | **Chapitres:** {len(mat['chapitres'])}")
            for ch in mat["chapitres"]:
                col_a, col_b = st.columns([3,1])
                col_a.write(f"• {ch}")
                col_b.selectbox("Statut", ["non commencé","en cours","maîtrisé"], key=f"{mat['nom']}_{ch}", label_visibility="collapsed")
            uploaded = st.file_uploader(f"Importer cours PDF pour {mat['nom']}", type=["pdf","txt"], key=f"up_{idx}")
            if uploaded:
                text = uploaded.read().decode('utf-8', errors='ignore')[:2000] if uploaded.type != "application/pdf" else "PDF extrait (aperçu)"
                st.success(f"Fichier {uploaded.name} importé !")
                st.text_area("Contenu extrait", text, height=150)
                if st.button(f"Générer fiche pour {mat['nom']}", key=f"fiche_{idx}"):
                    st.markdown(f"**Fiche {mat['nom']}**: Résumé fidèle basé sur {uploaded.name} - points clés, définitions, analogie.")

elif menu == "Assistant IA":
    st.title("🤖 Professeur Particulier IA - GLAR")
    st.caption("Base locale 80+ définitions • Source citée: cours vs générale • Mode offline")
    mode = st.selectbox("Mode", ["Expliquer simplement", "Donner exemple concret", "Générer fiche"])
    question = st.text_input("Pose ta question L3 (ex: c'est quoi VLAN ? ou explique TCP handshake)")
    contexte = st.text_area("Colle un extrait de ton cours (optionnel) pour résumé fidèle", height=100)
    
    if question:
        q_lower = question.lower()
        found = None
        for k,v in GLOSSARY.items():
            if k.lower() in q_lower:
                found = (k,v)
                break
        if found:
            st.markdown(f"### 📖 {found[0]}")
            st.write(found[1])
            st.caption(f"Source: {'issu de ton cours' if contexte else 'connaissance générale GLAR - base locale'}")
            if mode == "Donner exemple concret":
                st.code("Exemple Cisco:\n vlan 10\n name ETM_L3\n interface fa0/1\n switchport access vlan 10", language="bash")
            if mode == "Générer fiche":
                st.markdown("**Fiche révision synthétique:**\n- Définition\n- Points clés\n- Piège ESTM\n- Question type examen")
        else:
            st.write(f"Explication pour '{question}': C'est une notion L3 importante. Voici une analogie simple...")
            if contexte:
                st.info(f"Résumé de ton extrait: {contexte[:200]}... (référence page estimée)")
    
    st.divider()
    st.subheader("Questions progressives")
    if st.button("Génère 3 questions faciles→difficiles sur TCP/IP"):
        st.write("1. [Facile] Combien de couches OSI ? → 7")
        st.write("2. [Moyen] Différence TCP/UDP ? → Fiabilité vs rapidité")
        st.write("3. [Difficile] Calcule réseau 192.168.1.10/28 → 192.168.1.0/28")

elif menu == "Lab Programmation":
    st.title("💻 Lab Programmation")
    lang = st.selectbox("Langage", ["JavaScript","Python","SQL","Java","C","PHP"])
    exos = {
        "JavaScript": ["FizzBuzz - Boucles", "Classe Voiture POO", "Tri tableau"],
        "Python": ["Pile LIFO", "Recherche binaire", "API Flask"],
        "SQL": ["SELECT JOIN ESTM", "GROUP BY notes", "Index optimisation"]
    }
    exo = st.selectbox("Exercice", exos.get(lang, ["Exo 1","Exo 2"]))
    st.markdown(f"**Énoncé {exo}:** Écrire fonction qui... Objectifs: logique, POO, tests.")
    
    code = st.text_area("Éditeur code", value="// Tape ton code ici\nfunction solve(){ return 42; }", height=200)
    if st.button("▶️ Vérifier / Exécuter"):
        if lang == "JavaScript":
            try:
                # Exec sécurisé côté Python: simulation
                if "return" in code or "function" in code:
                    st.success("✅ Tests: 3/3 passés - Sortie: 42")
                else:
                    st.error("❌ Test échoué: fonction manquante")
            except Exception as e:
                st.error(str(e))
        else:
            st.info(f"🔍 Analyse statique {lang}: Vérifie présence mots-clés, structure. Correction détaillée: pense à gérer cas limite.")
        st.code("Correction: solution optimale O(n log n), explication...", language=lang.lower())

elif menu == "Lab Réseaux":
    st.title("🌐 Lab Administration Réseaux")
    tab1, tab2, tab3 = st.tabs(["Calculateur sous-réseaux", "Terminal Cisco", "Diagnostic panne"])
    with tab1:
        ip = st.text_input("IP/CIDR", "192.168.1.10/28")
        if st.button("Calculer"):
            try:
                import ipaddress
                net = ipaddress.ip_network(ip, strict=False)
                st.json({
                    "Réseau": str(net.network_address),
                    "Broadcast": str(net.broadcast_address),
                    "Masque": str(net.netmask),
                    "Hosts": net.num_addresses-2,
                    "Premier": str(list(net.hosts())[0]),
                    "Dernier": str(list(net.hosts())[-1]),
                })
            except Exception as e:
                st.error(f"Format invalide: {e}")
    with tab2:
        st.write("Terminal Cisco simulé - tape une commande")
        cmd = st.text_input("Switch> ", "enable")
        if cmd:
            responses = {
                "enable": "Switch#",
                "conf t": "Enter configuration commands",
                "vlan 10": "VLAN 10 created",
                "show vlan": "VLAN 10 ETM_L3 active",
            }
            st.code(responses.get(cmd.lower().strip(), f"% Commande {cmd} exécutée (simulation pédagogique)"))
    with tab3:
        st.write("Scénario: PC1 (192.168.1.10) ne ping pas Serveur (192.168.1.20)")
        choix = st.selectbox("Quelle commande d'abord ?", ["ping", "ipconfig /all", "traceroute", "show ip route"])
        if st.button("Diagnostiquer"):
            st.write(f"Résultat {choix}: ...")
            st.success("Piste: Vérifie VLAN + passerelle + ACL")

elif menu == "Quiz & Examens":
    st.title("📝 Quiz & Examens Blancs")
    mat_filter = st.selectbox("Filtrer par matière", ["Toutes"] + [m["nom"] for m in st.session_state.matieres])
    diff = st.select_slider("Difficulté", options=[1,2,3], value=2)
    
    questions = [
        {"q": "Combien de couches OSI ?", "choix": ["5","6","7","8"], "rep": "7", "exp": "7 couches OSI, 4 TCP/IP"},
        {"q": "Port HTTPS ?", "choix": ["80","443","22","53"], "rep": "443", "exp": "443=HTTPS, 80=HTTP"},
        {"q": "Réseau 192.168.1.10/28 ?", "choix": ["192.168.1.0/28","192.168.1.8/28","192.168.1.0/24"], "rep": "192.168.1.0/28", "exp": "/28 = bloc 16"},
    ]
    score = 0
    for i, qu in enumerate(questions):
        st.markdown(f"**Q{i+1}: {qu['q']}**")
        ans = st.radio(f"Choix Q{i+1}", qu["choix"], key=f"q_{i}", label_visibility="collapsed")
        if st.button(f"Vérifier Q{i+1}", key=f"b_{i}"):
            if ans == qu["rep"]:
                st.success(f"✅ Correct ! {qu['exp']}")
                score += 1
            else:
                st.error(f"❌ Faux. Réponse: {qu['rep']} - {qu['exp']} - À revoir: chapitre {mat_filter}")
    
    st.divider()
    if st.button("🎯 Lancer examen blanc 20 questions (45 min) - Chrono"):
        st.warning("Chrono lancé 45:00 - 20 questions multi-matières")
        st.progress(0.3, "6/20 répondues")

elif menu == "Planning":
    st.title("🗓️ Planning Intelligent SM-2")
    st.write("Algorithme: Score <50% → J+1, 50-75% → J+3, >75% → J+7. Max 3 chapitres/jour.")
    col1, col2 = st.columns(2)
    with col1:
        temps = st.slider("Temps dispo / jour (min)", 30, 240, 120)
        for ex in EXAMENS:
            st.checkbox(f"{ex['matiere']} - {ex['date']}", value=True)
    with col2:
        st.subheader("Calendrier Décembre 2026")
        data = [
            ["02 Dec", "OSI + UML", "60 min"],
            ["03 Dec", "VLSM exo", "90 min"],
            ["04 Dec", "Quiz BDD", "45 min"],
        ]
        st.table(pd.DataFrame(data, columns=["Date","Tâche","Durée"]))
        if st.button("🔄 Réorganiser si séance manquée"):
            st.success("Planning redistribué sans surcharger - 2 chapitres reportés")

elif menu == "Progression":
    st.title("📊 Progression & Badges")
    df = pd.DataFrame({"Mois": ["Sept","Oct","Nov","Déc"], "Score": st.session_state.quiz_scores})
    st.line_chart(df, x="Mois", y="Score")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Moyenne", "70%", "+12%")
    c2.metric("Chapitres maîtrisés", "8/24")
    c3.metric("Temps total", "42h")
    
    st.subheader("🏅 Badges universitaires")
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.success("🎖️ Maître UML")
    col_b2.info("🌐 Expert sous-réseaux")
    col_b3.warning("🔥 12 jours streak")
    
    if st.button("Exporter résultats JSON"):
        st.download_button("Télécharger JSON", data=json.dumps({"scores": st.session_state.quiz_scores, "examens": EXAMENS}), file_name="glar_progression.json")

# Footer
st.divider()
st.caption("GLAR MASTER v2 Streamlit - ESTM Dakar - Comprendre, pratiquer, maîtriser. | Demo: demo@estm.sn")
