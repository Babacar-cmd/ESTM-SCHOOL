
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json, os
from database import init_db, fetch_all, fetch_one, execute, get_storage_info
from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
init_db()
try:
    from data.seed import seed_all
    seed_all()
except:
    pass

if "page" not in st.session_state:
    st.session_state.page="Tableau de bord"
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers={}
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started={}
if "flash_idx" not in st.session_state:
    st.session_state.flash_idx=0
if "show_correction" not in st.session_state:
    st.session_state.show_correction={}
if "reveal" not in st.session_state:
    st.session_state.reveal=False

st.markdown("""
<style>
.main-header{background:linear-gradient(135deg,#1B4332 0%,#2D6A4F 100%);padding:24px;border-radius:12px;color:white;margin-bottom:16px}
div[data-testid="stMetric"]{background:#F5F7F3;padding:12px;border-radius:10px}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 🎓 {APP_NAME}\n*ESTM Dakar - L3 GLAR*")
    st.divider()
    pages=["Tableau de bord","Matières","Cours & Documents","Fiches","Quiz & QCM","Exercices","Assistant","Flashcards","Planning","Statistiques"]
    icons=["🏠","📚","📄","📝","❓","💻","🤖","🃏","🗓️","📊"]
    for i,p in enumerate(pages):
        if st.button(f"{icons[i]}  {p}", use_container_width=True, type="primary" if st.session_state.page==p else "secondary"):
            st.session_state.page=p
            st.rerun()
    st.divider()
    storage=get_storage_info()
    st.caption(f"Stockage: {storage['mode']}\nTaille: {storage['size_kb']} KB")
    st.caption(f"Version {APP_VERSION}")

def log_activite(type_, desc, matiere_id=None, duree=0):
    execute("INSERT INTO activites(type,description,matiere_id,duree,created_at) VALUES(?,?,?,?,?)",(type_,desc,matiere_id,duree,datetime.now().isoformat()))

page=st.session_state.page

if page=="Tableau de bord":
    st.markdown(f'<div class="main-header"><h1>{APP_NAME}</h1><p>Bienvenue ! Assistant personnel L3 GLAR - ESTM Dakar</p></div>', unsafe_allow_html=True)
    matieres=fetch_all("SELECT * FROM matieres")
    chapitres=fetch_all("SELECT * FROM chapitres")
    quiz_res=fetch_all("SELECT * FROM quiz_results")
    activites=fetch_all("SELECT * FROM activites ORDER BY created_at DESC LIMIT 10")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Matières", len(matieres))
    c2.metric("Chapitres", len(chapitres))
    c3.metric("Quiz réalisés", len(quiz_res))
    avg=round(sum([r["pourcentage"] for r in quiz_res])/len(quiz_res),1) if quiz_res else 0
    c4.metric("Taux moyen", f"{avg}%")
    st.divider()
    colA,colB=st.columns([2,1])
    with colA:
        st.subheader("Progression par matière")
        if quiz_res:
            df=pd.DataFrame(fetch_all("SELECT m.nom, qr.pourcentage FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id JOIN matieres m ON q.matiere_id=m.id"))
            if not df.empty:
                fig=px.bar(df, x="nom", y="pourcentage", color="pourcentage", color_continuous_scale="Greens")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas encore de quiz")
        st.subheader("Matières")
        for m in matieres[:6]:
            st.markdown(f"**{m['nom']}** - {m['statut']} - Obj {m['objectif']}%")
    with colB:
        st.subheader("Objectif quotidien")
        obj=st.slider("Minutes / jour", 15, 180, 60, step=15)
        st.progress(min(obj/120,1.0), text=f"{obj} min")
        st.subheader("Dernières activités")
        for a in activites:
            st.markdown(f"- {a['created_at'][:16]} : {a['type']} - {a['description']}")
        total_min=sum([a["duree"] for a in fetch_all("SELECT duree FROM activites")])
        st.metric("Minutes révisées", total_min)

elif page=="Matières":
    st.title("📚 Gestion des matières")
    tab1,tab2=st.tabs(["Liste","Ajouter / Modifier"])
    with tab1:
        matieres=fetch_all("SELECT * FROM matieres ORDER BY semestre, nom")
        for m in matieres:
            with st.expander(f"{m['nom']} - {m['semestre']} - {m['difficulte']} - {m['statut']}"):
                st.write(m["description"])
                chaps=fetch_all("SELECT * FROM chapitres WHERE matiere_id=?", (m["id"],))
                st.write(f"{len(chaps)} chapitres")
                col1,col2=st.columns(2)
                if col1.button(f"Supprimer", key=f"del_{m['id']}"):
                    if st.session_state.get(f"confirm_{m['id']}"):
                        execute("DELETE FROM matieres WHERE id=?", (m["id"],))
                        st.success("Supprimée"); st.rerun()
                    else:
                        st.session_state[f"confirm_{m['id']}"]=True
                        st.warning("Cliquez à nouveau pour confirmer")
                if col2.button(f"Maîtrisée", key=f"master_{m['id']}"):
                    execute("UPDATE matieres SET statut='Maîtrisé' WHERE id=?", (m["id"],)); st.rerun()
    with tab2:
        with st.form("mat_form"):
            nom=st.text_input("Nom *")
            desc=st.text_area("Description")
            sem=st.selectbox("Semestre", SEMESTRES)
            diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            statut=st.selectbox("Statut", STATUTS_REVISION)
            obj=st.slider("Objectif %", 50,100,80)
            submit=st.form_submit_button("Enregistrer")
            if submit:
                if not nom:
                    st.error("Nom obligatoire")
                else:
                    existing=fetch_one("SELECT id FROM matieres WHERE nom=?", (nom,))
                    if existing:
                        execute("UPDATE matieres SET description=?, semestre=?, difficulte=?, statut=?, objectif=? WHERE nom=?", (desc,sem,diff,statut,obj,nom))
                    else:
                        execute("INSERT INTO matieres(nom,description,semestre,difficulte,statut,objectif,created_at) VALUES(?,?,?,?,?,?,?)", (nom,desc,sem,diff,statut,obj,datetime.now().isoformat()))
                    st.success("Enregistrée"); log_activite("matiere", f"Création {nom}")

elif page=="Cours & Documents":
    st.title("📄 Cours & Documents")
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    tab_imp,tab_list,tab_search=st.tabs(["Importer","Mes cours","Recherche"])
    with tab_imp:
        with st.form("import_form"):
            titre=st.text_input("Titre du cours *")
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
            chapitres=fetch_all("SELECT * FROM chapitres WHERE matiere_id=?", (mat_map.get(mat_nom,0),)) if mat_map else []
            chap_map={c["titre"]: c["id"] for c in chapitres}
            chap_sel=st.selectbox("Chapitre (optionnel)", ["Aucun"]+list(chap_map.keys()))
            notes=st.text_area("Notes personnelles")
            contenu_manual=st.text_area("Contenu manuel (si pas de fichier)")
            uploaded=st.file_uploader("Fichier PDF/TXT/MD (max 15 Mo)", type=["pdf","txt","md"])
            submitted=st.form_submit_button("Enregistrer le cours")
            if submitted:
                if not titre:
                    st.error("Titre obligatoire")
                else:
                    text_content=contenu_manual
                    fname=None
                    if uploaded:
                        if uploaded.size>15*1024*1024:
                            st.error("Fichier trop volumineux")
                        else:
                            fname=uploaded.name
                            b=uploaded.read()
                            if fname.lower().endswith(".pdf"):
                                res=extract_text_from_pdf(b)
                            else:
                                res=extract_text_from_txt(b)
                            if res["success"]:
                                text_content=res["text"][:20000]
                                st.success(f"Texte extrait: {len(text_content)} caractères")
                            else:
                                st.warning(res["warning"])
                                text_content=contenu_manual
                    mat_id=mat_map.get(mat_nom)
                    chap_id=chap_map.get(chap_sel) if chap_sel!="Aucun" else None
                    execute("INSERT INTO cours(matiere_id,chapitre_id,titre,contenu,fichier_nom,notes,created_at) VALUES(?,?,?,?,?,?,?)",(mat_id,chap_id,titre,text_content,fname,notes,datetime.now().isoformat()))
                    st.success("Cours enregistré"); log_activite("cours", f"Import {titre}", mat_id, 15)
    with tab_list:
        cours=fetch_all("SELECT c.*, m.nom as matiere_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id ORDER BY c.created_at DESC")
        for c in cours:
            with st.expander(f"{c['titre']} - {c['matiere_nom'] or 'Sans matière'}"):
                st.text((c["contenu"][:2000] if c["contenu"] else "Pas de contenu"))
                if c["notes"]:
                    st.info(f"Notes: {c['notes']}")
                if st.button(f"Supprimer cours {c['id']}", key=f"del_c_{c['id']}"):
                    execute("DELETE FROM cours WHERE id=?", (c["id"],)); st.rerun()
    with tab_search:
        q=st.text_input("Rechercher un mot")
        if q:
            res=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? OR titre LIKE ?", (f"%{q}%", f"%{q}%"))
            st.write(f"{len(res)} résultats")
            for r in res:
                st.markdown(f"**{r['titre']}** - {(r['contenu'][:200] if r['contenu'] else '')}...")

elif page=="Fiches":
    st.title("📝 Fiches de révision")
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2,t3=st.tabs(["Créer auto depuis cours","Création manuelle","Mes fiches"])
    with t1:
        cours=fetch_all("SELECT c.*, m.nom as mat_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id")
        if not cours:
            st.info("Importez d'abord un cours")
        else:
            sel=st.selectbox("Choisir un cours", [f"{c['id']} - {c['titre']}" for c in cours])
            if st.button("Générer fiche automatique"):
                cid=int(sel.split(" - ")[0])
                cobj=fetch_one("SELECT * FROM cours WHERE id=?", (cid,))
                if cobj and cobj["contenu"]:
                    fiche_data=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,chapitre_id,titre,notions,definitions,points_cles,formules,exemples,erreurs,resume,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cobj["matiere_id"],cobj["chapitre_id"],f"Fiche - {cobj['titre']}",fiche_data["notions"],fiche_data["definitions"],fiche_data["points_cles"],fiche_data["formules"],fiche_data["exemples"],fiche_data["erreurs"],fiche_data["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée"); log_activite("fiche", f"Auto {cobj['titre']}", cobj["matiere_id"])
                else:
                    st.error("Contenu vide")
    with t2:
        with st.form("fiche_man"):
            titre=st.text_input("Titre fiche *")
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
            notions=st.text_area("Notions essentielles")
            definitions=st.text_area("Définitions")
            points=st.text_area("Points clés")
            formules=st.text_area("Formules / Syntaxes")
            exemples=st.text_area("Exemples pratiques")
            erreurs=st.text_area("Erreurs fréquentes")
            resume=st.text_area("Résumé final")
            sub=st.form_submit_button("Enregistrer fiche")
            if sub and titre:
                execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,formules,exemples,erreurs,resume,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,notions,definitions,points,formules,exemples,erreurs,resume,datetime.now().isoformat()))
                st.success("Fiche enregistrée")
    with t3:
        fiches=fetch_all("SELECT f.*, m.nom as mat_nom FROM fiches f LEFT JOIN matieres m ON f.matiere_id=m.id ORDER BY f.created_at DESC")
        for f in fiches:
            with st.expander(f"{f['titre']} - {f['mat_nom'] or ''}"):
                st.markdown(f"**Notions:**\n{f['notions']}")
                st.markdown(f"**Définitions:**\n{f['definitions']}")
                st.markdown(f"**Points clés:**\n{f['points_cles']}")
                st.markdown(f"**Formules:**\n{f['formules']}")
                st.markdown(f"**Exemples:**\n{f['exemples']}")
                st.markdown(f"**Erreurs:**\n{f['erreurs']}")
                st.markdown(f"**Résumé:**\n{f['resume']}")

elif page=="Quiz & QCM":
    st.title("❓ Quiz & QCM")
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    t_list,t_create,t_hist=st.tabs(["Passer un quiz","Créer un quiz","Historique"])
    with t_list:
        quizzes=fetch_all("SELECT q.*, m.nom as mat_nom FROM quiz q LEFT JOIN matieres m ON q.matiere_id=m.id")
        if not quizzes:
            st.info("Aucun quiz")
        else:
            q_sel=st.selectbox("Choisir quiz", [f"{q['id']} - {q['titre']} ({q['mat_nom']})" for q in quizzes])
            qid=int(q_sel.split(" - ")[0])
            questions=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            if not questions:
                st.warning("Pas de questions")
            else:
                mode=st.radio("Mode correction", ["À la fin","Après chaque question"], horizontal=True)
                nb_q=st.slider("Nombre de questions", 1, len(questions), len(questions))
                selected_q=questions[:nb_q]
                if st.button("Démarrer quiz"):
                    st.session_state.quiz_answers={}
                    st.session_state.quiz_started[qid]=datetime.now()
                    st.rerun()
                if qid in st.session_state.quiz_started:
                    st.divider()
                    for q in selected_q:
                        opts=json.loads(q["options"])
                        corrects=json.loads(q["reponses_correctes"])
                        st.markdown(f"**{q['question']}** *({q['difficulte']})*")
                        if q["type"]=="multiple":
                            ans=st.multiselect(f"Choix (plusieurs) {q['id']}", opts, key=f"q_{q['id']}")
                            mapped=[opts.index(a) for a in ans if a in opts]
                            st.session_state.quiz_answers[q["id"]]=mapped
                        else:
                            ans=st.radio(f"Choix {q['id']}", opts, key=f"q_{q['id']}", index=None)
                            if ans is not None:
                                mapped=[opts.index(ans)]
                                st.session_state.quiz_answers[q["id"]]=mapped
                        if mode=="Après chaque question" and q["id"] in st.session_state.quiz_answers:
                            given=st.session_state.quiz_answers[q["id"]]
                            if set(map(str,given))==set(map(str,corrects)):
                                st.success(f"Correct ! {q['explication']}")
                            else:
                                st.error(f"Raté. Attendu: {[opts[i] for i in corrects]} - {q['explication']}")
                    if st.button("Valider et voir score"):
                        res=calculate_quiz_score(st.session_state.quiz_answers, selected_q)
                        st.metric("Score /20", res["score20"])
                        st.metric("Pourcentage", f"{res['pct']:.1f}%")
                        start=st.session_state.quiz_started.get(qid, datetime.now())
                        elapsed=int((datetime.now()-start).total_seconds())
                        execute("INSERT INTO quiz_results(quiz_id,score,total,pourcentage,temps_sec,details,created_at) VALUES(?,?,?,?,?,?,?)",(qid,res["score20"],res["total"],res["pct"],elapsed,json.dumps(res["details"]),datetime.now().isoformat()))
                        log_activite("quiz", f"Quiz {qid} - {res['pct']:.0f}%", None, elapsed//60)
                        for q in selected_q:
                            opts=json.loads(q["options"])
                            corrects=json.loads(q["reponses_correctes"])
                            st.markdown(f"- Q: {q['question']} => Correct: {[opts[i] for i in corrects]}")
    with t_create:
        with st.form("create_quiz"):
            titre=st.text_input("Titre quiz *")
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
            diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            sub=st.form_submit_button("Créer quiz")
            if sub and titre:
                qid=execute("INSERT INTO quiz(matiere_id,titre,difficulte,created_at) VALUES(?,?,?,?)", (mat_map.get(mat_nom),titre,diff,datetime.now().isoformat()))
                st.success(f"Quiz créé id {qid}")
        st.divider()
        quizzes=fetch_all("SELECT * FROM quiz ORDER BY id DESC")
        if quizzes:
            q_sel2=st.selectbox("Ajouter question à", [f"{q['id']} - {q['titre']}" for q in quizzes], key="qadd")
            with st.form("add_q"):
                question=st.text_area("Question *")
                type_q=st.selectbox("Type", ["unique","multiple"])
                opt1=st.text_input("Option 1 *")
                opt2=st.text_input("Option 2 *")
                opt3=st.text_input("Option 3")
                opt4=st.text_input("Option 4")
                correct_str=st.text_input("Indices corrects (ex: 0 ou 0,1) *")
                expl=st.text_area("Explication")
                diff_q=st.selectbox("Difficulté question", NIVEAUX_DIFFICULTE, key="diff_q")
                sub_q=st.form_submit_button("Ajouter question")
                if sub_q and question and opt1 and opt2 and correct_str:
                    opts=[o for o in [opt1,opt2,opt3,opt4] if o]
                    try:
                        corrects=[int(x.strip()) for x in correct_str.split(",")]
                        qid=int(q_sel2.split(" - ")[0])
                        execute("INSERT INTO questions(quiz_id,question,type,options,reponses_correctes,explication,difficulte) VALUES(?,?,?,?,?,?,?)",(qid,question,type_q,json.dumps(opts),json.dumps(corrects),expl,diff_q))
                        st.success("Question ajoutée")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
    with t_hist:
        hist=fetch_all("SELECT qr.*, q.titre, m.nom as mat_nom FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id LEFT JOIN matieres m ON q.matiere_id=m.id ORDER BY qr.created_at DESC")
        if hist:
            df=pd.DataFrame(hist)
            st.dataframe(df[["created_at","titre","mat_nom","score","pourcentage","temps_sec"]])
            fig=px.line(df, x="created_at", y="pourcentage", color="mat_nom", title="Évolution scores")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas encore de résultats")

elif page=="Exercices":
    st.title("💻 Exercices pratiques")
    cat_filter=st.selectbox("Filtrer catégorie", ["Tous","POO","SQL","Réseaux","Linux","Algo","Web","UML"])
    if cat_filter=="Tous":
        exos=fetch_all("SELECT e.*, m.nom as mat_nom FROM exercices e LEFT JOIN matieres m ON e.matiere_id=m.id ORDER BY e.created_at DESC")
    else:
        exos=fetch_all("SELECT e.*, m.nom as mat_nom FROM exercices e LEFT JOIN matieres m ON e.matiere_id=m.id WHERE e.categorie=? ORDER BY e.created_at DESC", (cat_filter,))
    for e in exos:
        with st.expander(f"{e['titre']} - {e['categorie']} - {e['difficulte']} - {e['mat_nom'] or ''}"):
            st.markdown(f"**Énoncé:** {e['enonce']}")
            st.markdown(f"**Objectifs:** {e['objectifs']}")
            rep=st.text_area(f"Votre réponse {e['id']}", key=f"rep_{e['id']}")
            if st.button(f"Afficher correction {e['id']}", key=f"cor_{e['id']}"):
                st.session_state.show_correction[e['id']]=True
            if st.session_state.show_correction.get(e['id']):
                st.success(f"**Solution:**\n{e['solution']}")
                st.warning(f"**Erreurs à éviter:** {e['erreurs']}")
    st.divider()
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    st.subheader("Créer un exercice")
    with st.form("ex_form"):
        titre=st.text_input("Titre *")
        mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
        enonce=st.text_area("Énoncé *")
        objectifs=st.text_input("Objectifs")
        diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
        cat=st.text_input("Catégorie (POO, SQL, Réseaux...)")
        solution=st.text_area("Solution")
        erreurs=st.text_area("Erreurs à éviter")
        sub=st.form_submit_button("Enregistrer")
        if sub and titre and enonce:
            execute("INSERT INTO exercices(matiere_id,titre,enonce,objectifs,difficulte,solution,erreurs,categorie,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,enonce,objectifs,diff,solution,erreurs,cat,datetime.now().isoformat()))
            st.success("Exercice ajouté")

elif page=="Assistant":
    st.title("🤖 Assistant de révision intelligent")
    st.info("Assistant local - privilégie vos cours importés. Option OpenAI via st.secrets (facultatif). Sans clé, mode local actif.")
    query=st.text_input("Posez votre question (ex: Explique-moi la POO simplement)")
    if query:
        cours=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? LIMIT 5", (f"%{query.split()[0]}%",))
        context="\n".join([c["contenu"][:500] for c in cours]) if cours else ""
        if context:
            st.markdown(f"**Contexte trouvé dans vos cours:** {len(cours)} document(s)")
            st.text(context[:1000])
        qlow=query.lower()
        answer=None
        if "poo" in qlow or "orientée objet" in qlow:
            answer="**POO simplifiée:** Une classe = moule, objet = instance. Encapsulation, héritage, polymorphisme. Exemple: class Chien(Animal): def aboyer(self): print('wouaf')"
        elif "réseau" in qlow or "tcp" in qlow:
            answer="**Réseaux:** TCP fiable avec handshake, UDP rapide. VLAN isole broadcast. OSPF link-state."
        elif "sql" in qlow:
            answer="**SQL avancé:** Utilisez INDEX, EXPLAIN, RANK() OVER(PARTITION BY dept ORDER BY salaire DESC)"
        elif "45 minutes" in qlow or "séance" in qlow:
            answer="**Séance 45 min:** 10 min rappel, 20 min exo, 10 min QCM, 5 min fiche."
        else:
            answer=f"**Réponse locale:** Votre question '{query}' - cherchez dans vos fiches et cours. Importez vos PDFs pour enrichir le contexte. Configurez st.secrets['openai']['api_key'] pour IA externe."
            try:
                if "openai" in st.secrets:
                    st.warning("Clé OpenAI détectée - implémentez l'appel client ici.")
            except:
                pass
        if answer:
            st.markdown(answer)

elif page=="Flashcards":
    st.title("🃏 Flashcards & mémorisation")
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2=st.tabs(["Réviser","Gérer cartes"])
    with t2:
        with st.form("flash_form"):
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
            chapitres=fetch_all("SELECT * FROM chapitres WHERE matiere_id=?", (mat_map.get(mat_nom,0),)) if mat_map else []
            chap_map={c["titre"]: c["id"] for c in chapitres}
            chap_sel=st.selectbox("Chapitre", ["Aucun"]+list(chap_map.keys()))
            q=st.text_input("Question face avant *")
            r=st.text_area("Réponse face arrière *")
            sub=st.form_submit_button("Ajouter carte")
            if sub and q and r:
                execute("INSERT INTO flashcards(matiere_id,chapitre_id,question,reponse,statut,next_review,created_at) VALUES(?,?,?,?,?,?,?)",(mat_map.get(mat_nom),chap_map.get(chap_sel) if chap_sel!="Aucun" else None,q,r,"À revoir",spaced_next_review("À revoir"),datetime.now().isoformat()))
                st.success("Carte ajoutée")
        cards=fetch_all("SELECT f.*, m.nom as mat_nom FROM flashcards f LEFT JOIN matieres m ON f.matiere_id=m.id ORDER BY f.created_at DESC")
        for c in cards:
            with st.expander(f"{c['question'][:60]} - {c['statut']}"):
                st.write(f"Réponse: {c['reponse']}")
                if st.button(f"Supprimer carte {c['id']}", key=f"del_flash_{c['id']}"):
                    execute("DELETE FROM flashcards WHERE id=?", (c["id"],)); st.rerun()
    with t1:
        cards=fetch_all("SELECT * FROM flashcards ORDER BY next_review ASC")
        if not cards:
            st.info("Aucune carte")
        else:
            idx=st.session_state.flash_idx % len(cards)
            card=cards[idx]
            st.markdown(f"### Carte {idx+1}/{len(cards)} - {card['statut']}")
            st.markdown(f"**Q:** {card['question']}")
            if st.button("Révéler réponse"):
                st.session_state.reveal=True
            if st.session_state.get("reveal"):
                st.success(f"**R:** {card['reponse']}")
                c1,c2,c3=st.columns(3)
                if c1.button("À revoir"):
                    execute("UPDATE flashcards SET statut='À revoir', next_review=? WHERE id=?", (spaced_next_review("À revoir"), card["id"]))
                    st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()
                if c2.button("En cours"):
                    execute("UPDATE flashcards SET statut='En cours d'acquisition', next_review=? WHERE id=?", (spaced_next_review("En cours d'acquisition"), card["id"]))
                    st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()
                if c3.button("Maîtrisé"):
                    execute("UPDATE flashcards SET statut='Maîtrisé', next_review=? WHERE id=?", (spaced_next_review("Maîtrisé"), card["id"]))
                    st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()
            if st.button("Suivant"):
                st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()

elif page=="Planning":
    st.title("🗓️ Planning de révision")
    matieres=fetch_all("SELECT * FROM matieres")
    mat_map={m["nom"]: m["id"] for m in matieres}
    chapitres_all=fetch_all("SELECT * FROM chapitres")
    chap_map={f"{c['id']} - {c['titre']}": c["id"] for c in chapitres_all}
    with st.form("plan_form"):
        titre=st.text_input("Titre séance *")
        mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else [""])
        chap_sel=st.selectbox("Chapitre", ["Aucun"]+list(chap_map.keys()))
        date=st.date_input("Date", datetime.now().date())
        duree=st.number_input("Durée min", 15,240,60, step=15)
        priorite=st.selectbox("Priorité", ["Basse","Moyenne","Haute","Critique"])
        sub=st.form_submit_button("Ajouter séance")
        if sub and titre:
            execute("INSERT INTO planning(matiere_id,chapitre_id,titre,date,duree,priorite,statut,created_at) VALUES(?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),chap_map.get(chap_sel) if chap_sel!="Aucun" else None,titre,date.isoformat(),duree,priorite,"Prévu",datetime.now().isoformat()))
            st.success("Séance ajoutée")
    st.divider()
    sessions=fetch_all("SELECT p.*, m.nom as mat_nom FROM planning p LEFT JOIN matieres m ON p.matiere_id=m.id ORDER BY p.date ASC")
    today=datetime.now().date()
    retard=[s for s in sessions if datetime.fromisoformat(s["date"]).date() < today and s["statut"]!="Terminée"]
    if retard:
        st.warning(f"{len(retard)} séances en retard")
    for s in sessions:
        col1,col2,col3=st.columns([3,1,1])
        col1.markdown(f"**{s['titre']}** - {s['mat_nom'] or ''} - {s['date']} - {s['duree']}min - {s['priorite']} - {s['statut']}")
        if col2.button("Terminée", key=f"done_{s['id']}"):
            execute("UPDATE planning SET statut='Terminée' WHERE id=?", (s["id"],))
            log_activite("planning", f"Séance terminée {s['titre']}", s["matiere_id"], s["duree"]); st.rerun()
        if col3.button("Suppr", key=f"del_plan_{s['id']}"):
            execute("DELETE FROM planning WHERE id=?", (s["id"],)); st.rerun()
    if st.button("Générer suggestion selon faiblesses"):
        faibles=fetch_all("SELECT m.id, m.nom FROM matieres m WHERE m.statut!='Maîtrisé' LIMIT 5")
        for i,fm in enumerate(faibles):
            d=(today + timedelta(days=i)).isoformat()
            execute("INSERT INTO planning(matiere_id,titre,date,duree,priorite,statut,created_at) VALUES(?,?,?,?,?,?,?)",(fm["id"],f"Révision {fm['nom']}",d,60,"Haute","Prévu",datetime.now().isoformat()))
        st.success("Planning généré"); st.rerun()

elif page=="Statistiques":
    st.title("📊 Statistiques & Progression")
    quiz_res=fetch_all("SELECT qr.*, q.titre, m.nom as mat_nom FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id LEFT JOIN matieres m ON q.matiere_id=m.id")
    if not quiz_res:
        st.info("Pas encore de données")
    else:
        df=pd.DataFrame(quiz_res)
        c1,c2,c3=st.columns(3)
        c1.metric("Score moyen /20", round(df["score"].mean(),2))
        c2.metric("Meilleur %", f"{df['pourcentage'].max():.1f}%")
        c3.metric("Temps total quiz min", int(df["temps_sec"].sum()//60))
        fig1=px.line(df, x="created_at", y="pourcentage", color="mat_nom", title="Évolution des scores")
        st.plotly_chart(fig1, use_container_width=True)
        fig2=px.bar(df.groupby("mat_nom")["pourcentage"].mean().reset_index(), x="mat_nom", y="pourcentage", title="Taux réussite par matière")
        st.plotly_chart(fig2, use_container_width=True)
        chaps=fetch_all("SELECT statut, COUNT(*) as c FROM chapitres GROUP BY statut")
        if chaps:
            df_c=pd.DataFrame(chaps)
            fig3=px.pie(df_c, names="statut", values="c", title="Chapitres par statut")
            st.plotly_chart(fig3, use_container_width=True)
        st.subheader("Recommandations")
        low=df[df["pourcentage"]<60]
        if not low.empty:
            for _, row in low.iterrows():
                st.warning(f"À revoir: {row['mat_nom']} - {row['titre']} ({row['pourcentage']}%)")
        else:
            st.success("Bonne progression !")

st.divider()
st.caption("GLAR Revision Hub - ESTM Dakar - SQLite local (temporaire sur Streamlit Cloud). Pour persistance durable, configurez PostgreSQL (voir README).")
