import os
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Smart Grocery List • Studio Visual Pro",
    page_icon="⚡",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Design System - Palette Colorée et Dynamique (Vibrant Light)
PALETTE = {
    "bg": "#F1F5F9",
    "header_bg": "#FFFFFF",
    "card_bg": "#FFFFFF",
    "card_hover": "#F8FAFC",
    "card_selected": "#EEF2FF",
    "border_card": "#CBD5E1",
    "border_selected": "#6366F1",
    "text_main": "#0F172A",
    "text_muted": "#475569",
    "accent": "#4F46E5",
    "accent_hover": "#4338CA",
    "vege_txt": "#065F46", "vege_bg": "#D1FAE5",
    "pesce_txt": "#1E40AF", "pesce_bg": "#DBEAFE",
    "viande_txt": "#991B1B", "viande_bg": "#FEE2E2",
    "postit_bg": "#FEF08A",
    "postit_txt": "#713F12",
    "postit_border": "#F59E0B"
}

COULEURS_EMOJI_BG = {
    "Recettes": "#E0E7FF",
    "Fruits": "#FFEDD5",
    "Légumes": "#D1FAE5",
    "Épicerie": "#FEF3C7",
    "Frais": "#E0F2FE",
    "Boissons": "#FCE7F3",
}

# Dictionnaire de correspondance Mot-Clé -> Émoticône
EMOJI_KEYWORDS = [
    (["poulet", "dinde", "volaille"], "🍗"),
    (["boeuf", "bœuf", "steak", "haché", "veau", "carnivore"], "🥩"),
    (["porc", "bacon", "jambon", "lardons", "saucisse", "chorizo"], "🥓"),
    (["burger"], "🍔"),
    (["pizza"], "🍕"),
    (["poisson", "saumon", "thon", "cabillaud", "truite", "colin", "pavé"], "🐟"),
    (["crevette", "moule", "fruit de mer", "saint-jacques"], "🦐"),
    (["tarte", "quiche"], "🥧"),
    (["soupe", "velouté", "potage", "bouillon"], "🥣"),
    (["pâte", "pates", "spaghetti", "penne", "lasagne", "bolognaise"], "🍝"),
    (["riz", "risotto", "dahl", "dal"], "🍚"),
    (["salade", "caesar"], "🥗"),
    (["curry"], "🍛"),
    (["gâteau", "gateau", "cake", "chocolat", "dessert", "tarte sucrée"], "🍰"),
    (["pomme"], "🍎"),
    (["banane"], "🍌"),
    (["fraise", "framboise", "baie", "myrtille"], "🍓"),
    (["citron"], "🍋"),
    (["orange", "clementine", "mandarine"], "🍊"),
    (["poire"], "🍐"),
    (["raisin"], "🍇"),
    (["avocat"], "🥑"),
    (["ananas"], "🍍"),
    (["pêche", "abricot"], "🍑"),
    (["courgette"], "🥒"),
    (["carotte"], "🥕"),
    (["tomate"], "🍅"),
    (["pomme de terre", "patate", "frite"], "🥔"),
    (["poivron"], "🫑"),
    (["champignon"], "🍄"),
    (["brocoli", "chou"], "🥦"),
    (["oignon", "ail", "échalote"], "🧅"),
    (["épinard", "epinard", "salade", "laitue"], "🥬"),
    (["aubergine"], "🍆"),
    (["maïs", "mais"], "🌽"),
    (["concombre"], "🥒"),
    (["oeuf", "œuf"], "🥚"),
    (["fromage", "comté", "emmental", "mozzarella", "parmesan", "raclette", "chèvre"], "🧀"),
    (["lait", "crème", "creme", "yaourt"], "🥛"),
    (["beurre"], "🧈"),
    (["pain", "baguette", "toast", "brioche"], "🍞"),
    (["huile", "vinaigre", "olive"], "🫒"),
    (["farine", "sucre", "sel", "poivre", "épice"], "🧂"),
    (["chocolat"], "🍫"),
    (["miel", "confiture"], "🍯"),
    (["eau"], "💧"),
    (["jus"], "🧃"),
    (["café", "cafe"], "☕"),
    (["thé", "the"], "🍵"),
    (["bière", "biere"], "🍺"),
    (["vin"], "🍷"),
    (["soda", "coca"], "🥤")
]

EMOJI_CATEGORIES_DEFAULT = {
    "Recettes": "🍽️",
    "Fruits": "🍎",
    "Légumes": "🥦",
    "Épicerie": "📦",
    "Frais": "🧀",
    "Boissons": "🥤"
}

def obtenir_emoticon_item(item_name, sheet_name=""):
    nom_lower = item_name.lower()
    for mots, emoji in EMOJI_KEYWORDS:
        if any(m in nom_lower for m in mots):
            return emoji
    return EMOJI_CATEGORIES_DEFAULT.get(sheet_name, "🛒")

def extraire_couleurs_items_ods(chemin_fichier, sheet_name="Recettes"):
    couleurs = {}
    ns = {
        'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
        'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
    }
    try:
        with zipfile.ZipFile(chemin_fichier, 'r') as z:
            content_xml = z.read('content.xml')
            styles_xml = z.read('styles.xml') if 'styles.xml' in z.namelist() else b''

        styles_map = {}
        def analyser_styles_tree(root_elem):
            if root_elem is None: return
            for elem in root_elem.iter():
                if elem.tag.endswith('style'):
                    name = elem.attrib.get(f"{{{ns['style']}}}name")
                    if name:
                        for child in elem:
                            if child.tag.endswith('table-cell-properties'):
                                bg = child.attrib.get(f"{{{ns['fo']}}}background-color")
                                if bg: styles_map[name] = bg

        root_content = ET.fromstring(content_xml)
        root_styles = ET.fromstring(styles_xml) if styles_xml else None
        analyser_styles_tree(root_content)
        analyser_styles_tree(root_styles)

        for table in root_content.findall('.//table:table', ns):
            if table.attrib.get(f"{{{ns['table']}}}name") == sheet_name:
                first_row = table.find('.//table:table-row', ns)
                if first_row is not None:
                    for cell in first_row.findall('.//table:table-cell', ns):
                        style_name = cell.attrib.get(f"{{{ns['table']}}}style-name")
                        text_elems = cell.findall('.//text:p', ns)
                        cell_text = " ".join([t.text for t in text_elems if t.text]).strip()
                        if cell_text and style_name in styles_map:
                            couleurs[cell_text] = styles_map[style_name]
    except Exception as e:
        print(f"ℹ️ Info extraction couleurs : {e}")
    return couleurs

def analyser_regime_couleur(hex_code):
    if not hex_code or not isinstance(hex_code, str):
        return None, None, None
    hex_code = hex_code.strip()
    if hex_code.startswith('#') and len(hex_code) >= 7:
        hex_code = hex_code[:7]
    else:
        return None, None, None
    try:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        if (r > 240 and g > 240 and b > 240) or (r < 30 and g < 30 and b < 30):
            return None, None, None
        if g >= r and g > b:
            return "🥦 Végé", PALETTE["vege_txt"], PALETTE["vege_bg"]
        elif b > r and b >= g:
            return "🐟 Pescé", PALETTE["pesce_txt"], PALETTE["pesce_bg"]
        elif r > g and r > b:
            return "🥩 Viande", PALETTE["viande_txt"], PALETTE["viande_bg"]
    except ValueError:
        pass
    return None, None, None

def deviner_regime_par_nom(nom):
    nom_lower = nom.lower()
    mots_pesce = ["poisson", "saumon", "thon", "cabillaud", "crevette", "truite", "moule", "sardine", "colin", "pavé"]
    if any(m in nom_lower for m in mots_pesce):
        return "🐟 Pescé", PALETTE["pesce_txt"], PALETTE["pesce_bg"]
    mots_viande = ["poulet", "boeuf", "bœuf", "porc", "bacon", "jambon", "steak", "haché", "canard", "dinde", "lardons", "bolognaise", "saucisse", "veau", "chorizo", "carnivore"]
    if any(m in nom_lower for m in mots_viande):
        return "🥩 Viande", PALETTE["viande_txt"], PALETTE["viande_bg"]
    mots_vege = ["dahl", "dal", "courgette", "legume", "légume", "tofu", "vege", "végé", "lentille", "épinard", "epinard", "aubergine", "tarte", "quiche", "soupe", "velouté", "gratin", "pâte", "pates", "riz", "salade", "gâteau"]
    if any(m in nom_lower for m in mots_vege):
        return "🥦 Végé", PALETTE["vege_txt"], PALETTE["vege_bg"]
    return None, None, None

fichiers_ods = [f for f in os.listdir(BASE_DIR) if f.endswith('.ods')]
if not fichiers_ods:
    st.error("❌ Aucun fichier LibreOffice (.ods) trouvé dans le dossier !")
    st.stop()

chemin_fichier = os.path.join(BASE_DIR, fichiers_ods[0])

@st.cache_data
def charger_donnees(chemin):
    dataframes = {}
    try:
        excel_file = pd.ExcelFile(chemin)
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(chemin, sheet_name=sheet)
            if not df.empty:
                dataframes[sheet] = df
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
    return dataframes

dataframes = charger_donnees(chemin_fichier)
couleurs_recettes = extraire_couleurs_items_ods(chemin_fichier, "Recettes")

if "selections" not in st.session_state:
    st.session_state.selections = {}
if "recettes_vues" not in st.session_state:
    st.session_state.recettes_vues = set()
if "recettes_actuelles_6" not in st.session_state:
    st.session_state.recettes_actuelles_6 = []
if "pages_standard" not in st.session_state:
    st.session_state.pages_standard = {}
if "quantites_custom" not in st.session_state:
    st.session_state.quantites_custom = {}
if "articles_perso" not in st.session_state:
    st.session_state.articles_perso = []

toutes_recettes = list(dataframes["Recettes"].columns[1:]) if "Recettes" in dataframes else []

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("⚡ Smart Grocery List • Studio Visual Pro")
with header_col2:
    nb_sel = len(st.session_state.selections)
    st.markdown(
        f"<div style='background-color:#EEF2FF; border:1.5px solid #C7D2FE; border-radius:20px; padding:10px 20px; text-align:center;'>"
        f"<span style='color:#4338CA; font-weight:bold; font-size:16px;'>{nb_sel} item{'s' if nb_sel > 1 else ''} sélectionné{'s' if nb_sel > 1 else ''}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

noms_onglets = list(dataframes.keys()) + ["📋 Ma Liste de Courses"]
onglets = st.tabs(noms_onglets)

if "Recettes" in dataframes:
    idx_recettes = list(dataframes.keys()).index("Recettes")
    with onglets[idx_recettes]:
        col_main_recettes, col_postit = st.columns([3, 1])
        
        with col_main_recettes:
            top_bar = st.columns([2, 3])
            with top_bar[0]:
                if st.button("🎲 Proposer 6 autres recettes", use_container_width=True):
                    non_vues = [r for r in toutes_recettes if r not in st.session_state.recettes_vues]
                    if len(non_vues) < 6:
                        st.session_state.recettes_vues.clear()
                        non_vues = [r for r in toutes_recettes if ("Recettes", r) not in st.session_state.selections]
                    st.session_state.recettes_actuelles_6 = non_vues[:6]
                    for r in st.session_state.recettes_actuelles_6:
                        st.session_state.recettes_vues.add(r)
                    st.rerun()
            
            if not st.session_state.recettes_actuelles_6 and toutes_recettes:
                st.session_state.recettes_actuelles_6 = toutes_recettes[:6]
                for r in st.session_state.recettes_actuelles_6:
                    st.session_state.recettes_vues.add(r)

            with top_bar[1]:
                st.markdown(
                    "<div style='display:flex; gap:10px; justify-content:flex-end; align-items:center; height:100%;'>"
                    f"<span style='background-color:{PALETTE['vege_bg']}; color:{PALETTE['vege_txt']}; padding:6px 12px; border-radius:12px; font-weight:bold; font-size:13px;'>🥦 Végé</span>"
                    f"<span style='background-color:{PALETTE['pesce_bg']}; color:{PALETTE['pesce_txt']}; padding:6px 12px; border-radius:12px; font-weight:bold; font-size:13px;'>🐟 Pescé</span>"
                    f"<span style='background-color:{PALETTE['viande_bg']}; color:{PALETTE['viande_txt']}; padding:6px 12px; border-radius:12px; font-weight:bold; font-size:13px;'>🥩 Viande</span>"
                    "</div>",
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            lignes_recettes = [st.session_state.recettes_actuelles_6[i:i+3] for i in range(0, len(st.session_state.recettes_actuelles_6), 3)]
            for ligne in lignes_recettes:
                cols_card = st.columns(3)
                for c_idx, item_name in enumerate(ligne):
                    with cols_card[c_idx]:
                        cle = ("Recettes", item_name)
                        est_selectionne = cle in st.session_state.selections
                        emoji = obtenir_emoticon_item(item_name, "Recettes")
                        
                        label_reg, txt_c, bg_c = None, None, None
                        if item_name in couleurs_recettes:
                            label_reg, txt_c, bg_c = analyser_regime_couleur(couleurs_recettes[item_name])
                        if not label_reg:
                            label_reg, txt_c, bg_c = deviner_regime_par_nom(item_name)

                        card_bg_color = PALETTE["card_selected"] if est_selectionne else PALETTE["card_bg"]
                        border_col = PALETTE["border_selected"] if est_selectionne else PALETTE["border_card"]
                        
                        # Correction de la syntaxe du badge et des symboles
                        badge_html = f"<span style='background-color:{bg_c}; color:{txt_c}; padding:3px 8px; border-radius:10px; font-size:11px; font-weight:bold;'>{label_reg}</span>" if label_reg else "<span></span>"
                        check_symbol = '✓' if est_selectionne else '○'
                        check_color = PALETTE['border_selected'] if est_selectionne else '#94A3B8'

                        st.markdown(
                            f"<div style='background-color:{card_bg_color}; border:2px solid {border_col}; border-radius:18px; padding:16px; text-align:center; min-height:190px; display:flex; flex-direction:column; justify-content:space-between;'>"
                            f"<div>"
                            f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                            f"{badge_html}"
                            f"<span style='font-size:18px; font-weight:bold; color:{check_color};'>{check_symbol}</span>"
                            f"</div>"
                            f"<div style='background-color:{COULEURS_EMOJI_BG['Recettes']}; border-radius:16px; width:54px; height:54px; display:flex; align-items:center; justify-content:center; margin:10px auto;'>"
                            f"<span style='font-size:30px;'>{emoji}</span>"
                            f"</div>"
                            f"<div style='font-weight:bold; font-size:14px; color:{PALETTE['text_main']};'>{item_name}</div>"
                            f"</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1:
                            btn_label = "Désélectionner" if est_selectionne else "Sélectionner"
                            if st.button(btn_label, key=f"sel_rec_{item_name}", use_container_width=True):
                                if est_selectionne:
                                    del st.session_state.selections[cle]
                                else:
                                    st.session_state.selections[cle] = 1
                                st.rerun()
                        with c_btn2:
                            if st.button("🔍 Ingrédients", key=f"dt_rec_{item_name}", use_container_width=True):
                                @st.dialog(f"Composition : {item_name}", width="large")
                                def afficher_popup_ingredients(sh, itm):
                                    df_s = dataframes[sh]
                                    col_ing = df_s.columns[0]
                                    st.markdown(f"### {obtenir_emoticon_item(itm, sh)} {itm}")
                                    st.markdown(f"**Catégorie :** {sh}")
                                    st.markdown("---")
                                    ingredients_trouves = []
                                    for _, row in df_s.iterrows():
                                        ing = row[col_ing]
                                        val = row[itm]
                                        if pd.notna(val) and val != 0 and str(val).strip() != "":
                                            qte_s = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                                            ingredients_trouves.append((ing, qte_s))
                                    if not ingredients_trouves:
                                        st.info("Aucun ingrédient spécifique renseigné.")
                                    else:
                                        for ing_n, q_s in ingredients_trouves:
                                            i_em = obtenir_emoticon_item(ing_n)
                                            st.markdown(f"- **{i_em} {ing_n}** : x {q_s}")
                                afficher_popup_ingredients("Recettes", item_name)

        with col_postit:
            st.markdown(
                f"<div style='background-color:{PALETTE['postit_bg']}; border:2px solid {PALETTE['postit_border']}; border-radius:18px; padding:20px;'>"
                f"<h3 style='color:{PALETTE['postit_txt']}; margin-top:0; font-size:18px;'>📌 MES RECETTES</h3>",
                unsafe_allow_html=True
            )
            recettes_choisies = [item for (sheet, item) in st.session_state.selections.keys() if sheet == "Recettes"]
            st.markdown(f"<p style='color:#B45309; font-weight:bold; font-size:14px;'>{len(recettes_choisies)} recette(s) sélectionnée(s)</p>", unsafe_allow_html=True)
            
            if not recettes_choisies:
                st.info("Aucune recette cochée.")
            else:
                for r in recettes_choisies:
                    em = obtenir_emoticon_item(r, "Recettes")
                    st.markdown(f"• {em} **{r}**")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if recettes_choisies:
                if st.button("👁️ Prévisualiser & Copier", use_container_width=True):
                    texte_rec = "🍽️ MES RECETTES SÉLECTIONNÉES :\n" + "═" * 35 + "\n"
                    for r in recettes_choisies:
                        texte_rec += f"• {obtenir_emoticon_item(r, 'Recettes')} {r}\n"
                    @st.dialog("Aperçu - Liste des Recettes")
                    def pop_preview_rec():
                        st.text_area("Texte :", value=texte_rec, height=200)
                        if st.button("📋 Copier dans le presse-papier"):
                            st.toast("Texte prêt à être copié !")
                    pop_preview_rec()

for idx, sheet_name in enumerate(dataframes.keys()):
    if sheet_name == "Recettes":
        continue
    with onglets[idx]:
        df = dataframes[sheet_name]
        items = list(df.columns[1:])
        total_items = len(items)
        items_par_page = 12
        total_pages = max(1, (total_items + items_par_page - 1) // items_par_page)

        if sheet_name not in st.session_state.pages_standard:
            st.session_state.pages_standard[sheet_name] = 0

        page_actuelle = st.session_state.pages_standard[sheet_name]
        if page_actuelle >= total_pages:
            page_actuelle = 0
            st.session_state.pages_standard[sheet_name] = 0

        c_p1, c_p2, c_p3 = st.columns([1, 2, 1])
        with c_p1:
            if st.button("⬅️ 12 Précédents", key=f"prev_{sheet_name}", disabled=(page_actuelle == 0), use_container_width=True):
                st.session_state.pages_standard[sheet_name] -= 1
                st.rerun()
        with c_p2:
            start_idx = page_actuelle * items_par_page
            end_idx = min(start_idx + items_par_page, total_items)
            st.markdown(f"<div style='text-align:center; font-weight:bold; font-size:16px; padding-top:8px;'>Page {page_actuelle + 1} / {total_pages} ({start_idx + 1}-{end_idx} sur {total_items})</div>", unsafe_allow_html=True)
        with c_p3:
            if st.button("12 Suivants ➡️", key=f"next_{sheet_name}", disabled=(page_actuelle >= total_pages - 1), use_container_width=True):
                st.session_state.pages_standard[sheet_name] += 1
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        items_page = items[start_idx:end_idx]
        lignes_std = [items_page[i:i+4] for i in range(0, len(items_page), 4)]

        for ligne in lignes_std:
            cols_std = st.columns(4)
            for c_idx, item_name in enumerate(ligne):
                with cols_std[c_idx]:
                    cle = (sheet_name, item_name)
                    est_selectionne = cle in st.session_state.selections
                    emoji = obtenir_emoticon_item(item_name, sheet_name)
                    
                    card_bg_color = PALETTE["card_selected"] if est_selectionne else PALETTE["card_bg"]
                    border_col = PALETTE["border_selected"] if est_selectionne else PALETTE["border_card"]
                    
                    check_symbol_std = '✓' if est_selectionne else '○'
                    check_color_std = PALETTE['border_selected'] if est_selectionne else '#94A3B8'

                    st.markdown(
                        f"<div style='background-color:{card_bg_color}; border:2px solid {border_col}; border-radius:18px; padding:16px; text-align:center; min-height:180px; display:flex; flex-direction:column; justify-content:space-between;'>"
                        f"<div>"
                        f"<div style='display:flex; justify-content:flex-end; align-items:center;'>"
                        f"<span style='font-size:18px; font-weight:bold; color:{check_color_std};'>{check_symbol_std}</span>"
                        f"</div>"
                        f"<div style='background-color:{COULEURS_EMOJI_BG.get(sheet_name, '#F1F5F9')}; border-radius:16px; width:54px; height:54px; display:flex; align-items:center; justify-content:center; margin:10px auto;'>"
                        f"<span style='font-size:30px;'>{emoji}</span>"
                        f"</div>"
                        f"<div style='font-weight:bold; font-size:14px; color:{PALETTE['text_main']};'>{item_name}</div>"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        btn_label = "Désélectionner" if est_selectionne else "Sélectionner"
                        if st.button(btn_label, key=f"sel_{sheet_name}_{item_name}", use_container_width=True):
                            if est_selectionne:
                                del st.session_state.selections[cle]
                            else:
                                st.session_state.selections[cle] = 1
                            st.rerun()
                    with c_btn2:
                        if st.button("🔍 Ingrédients", key=f"dt_{sheet_name}_{item_name}", use_container_width=True):
                            @st.dialog(f"Composition : {item_name}", width="large")
                            def afficher_popup_std(sh, itm):
                                df_s = dataframes[sh]
                                col_ing = df_s.columns[0]
                                st.markdown(f"### {obtenir_emoticon_item(itm, sh)} {itm}")
                                st.markdown(f"**Catégorie :** {sh}")
                                st.markdown("---")
                                ingredients_trouves = []
                                for _, row in df_s.iterrows():
                                    ing = row[col_ing]
                                    val = row[itm]
                                    if pd.notna(val) and val != 0 and str(val).strip() != "":
                                        qte_s = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val)
                                        ingredients_trouves.append((ing, qte_s))
                                if not ingredients_trouves:
                                    st.info("Aucun ingrédient spécifique renseigné.")
                                else:
                                    for ing_n, q_s in ingredients_trouves:
                                        i_em = obtenir_emoticon_item(ing_n)
                                        st.markdown(f"- **{i_em} {ing_n}** : x {q_s}")
                            afficher_popup_std(sheet_name, item_name)

with onglets[-1]:
    col_panel_gauche, col_panel_droit = st.columns([1, 2])

    totaux_ingredients = {}
    for (sheet_name, item_col), multiplier in st.session_state.selections.items():
        df = dataframes[sheet_name]
        col_ingredients = df.columns[0]
        for _, row in df.iterrows():
            ing = row[col_ingredients]
            valeur = row[item_col]
            if pd.notna(valeur) and valeur != 0:
                try:
                    qte_numerique = float(valeur) * multiplier
                    totaux_ingredients[ing] = totaux_ingredients.get(ing, 0) + qte_numerique
                except ValueError:
                    str_val = f"{valeur}"
                    totaux_ingredients[ing] = f"{totaux_ingredients[ing]} + {str_val}" if ing in totaux_ingredients else str_val

    for art in st.session_state.articles_perso:
        totaux_ingredients[art] = totaux_ingredients.get(art, 0) + 1

    for ing in list(totaux_ingredients.keys()):
        if ing in st.session_state.quantites_custom:
            totaux_ingredients[ing] = st.session_state.quantites_custom[ing]

    with col_panel_gauche:
        st.markdown(
            f"<div style='background-color:{PALETTE['header_bg']}; border:1.5px solid {PALETTE['border_card']}; border-radius:18px; padding:20px;'>"
            f"<h2 style='color:{PALETTE['text_main']}; margin-top:0;'>Actions & Options</h2>",
            unsafe_allow_html=True
        )
        
        if st.button("➕ Ajouter un article perso", use_container_width=True):
            @st.dialog("Ajouter un article hors-liste")
            def pop_ajout_perso():
                nom_perso = st.text_input("Nom de l'article :")
                if st.button("Confirmer l'ajout"):
                    if nom_perso and nom_perso.strip():
                        art_c = nom_perso.strip()
                        if art_c not in st.session_state.articles_perso:
                            st.session_state.articles_perso.append(art_c)
                        st.rerun()
            pop_ajout_perso()

        if st.button("👁️ Prévisualiser & Copier", use_container_width=True):
            recettes_choisies = [item for (sheet, item) in st.session_state.selections.keys() if sheet == "Recettes"]
            texte_complet = ""
            if recettes_choisies:
                texte_complet += "🍽️ RECETTES AU MENU CETTE SEMAINE\n" + "═" * 40 + "\n"
                for r in recettes_choisies:
                    texte_complet += f" • {obtenir_emoticon_item(r, 'Recettes')} {r}\n"
                texte_complet += "\n"
            texte_complet += "📌 LISTE DE COURSES AGRÉGÉE\n" + "═" * 40 + "\n\n"
            for ing, qte in sorted(totaux_ingredients.items()):
                q_str = str(int(qte)) if isinstance(qte, float) and qte.is_integer() else str(qte)
                texte_complet += f" ☐  {obtenir_emoticon_item(ing)} {ing:<28} (x{q_str})\n"

            @st.dialog("Aperçu - Liste Global & Recettes")
            def pop_preview_global():
                st.text_area("Texte prêt à copier :", value=texte_complet, height=300)
                st.info("Vous pouvez copier le texte ci-dessus.")
            pop_preview_global()

        if st.button("💾 Enregistrer en Fichier (.txt)", use_container_width=True):
            recettes_choisies = [item for (sheet, item) in st.session_state.selections.keys() if sheet == "Recettes"]
            texte_complet = ""
            if recettes_choisies:
                texte_complet += "🍽️ RECETTES AU MENU CETTE SEMAINE\n" + "═" * 40 + "\n"
                for r in recettes_choisies:
                    texte_complet += f" • {obtenir_emoticon_item(r, 'Recettes')} {r}\n"
                texte_complet += "\n"
            texte_complet += "📌 LISTE DE COURSES AGRÉGÉE\n" + "═" * 40 + "\n\n"
            for ing, qte in sorted(totaux_ingredients.items()):
                q_str = str(int(qte)) if isinstance(qte, float) and qte.is_integer() else str(qte)
                texte_complet += f" ☐  {obtenir_emoticon_item(ing)} {ing:<28} (x{q_str})\n"

            st.download_button(
                label="Télécharger le fichier .txt",
                data=texte_complet,
                file_name="liste_de_courses.txt",
                mime="text/plain",
                use_container_width=True
            )

        if st.button("🗑️ Remettre à zéro tout", use_container_width=True):
            st.session_state.selections.clear()
            st.session_state.quantites_custom.clear()
            st.session_state.articles_perso.clear()
            st.session_state.recettes_vues.clear()
            st.rerun()

        st.markdown(f"<br><p style='color:{PALETTE['text_muted']}; font-size:14px;'>Cartes cochées : {len(st.session_state.selections)}<br>Articles distincts : {len(totaux_ingredients)}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_panel_droit:
        st.markdown(
            f"<div style='background-color:{PALETTE['header_bg']}; border:1.5px solid {PALETTE['border_card']}; border-radius:18px; padding:20px;'>"
            f"<h3 style='color:{PALETTE['text_main']}; margin-top:0;'>🛒 Articles à Acheter</h3>",
            unsafe_allow_html=True
        )

        if not totaux_ingredients:
            st.info("⚠️ Votre liste est vide. Cochez des éléments dans les onglets précédents.")
        else:
            for ing, qte in sorted(totaux_ingredients.items()):
                ing_emoji = obtenir_emoticon_item(ing)
                r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([3, 1, 1, 1, 1])
                
                with r_col1:
                    st.markdown(f"**{ing_emoji} {ing}**")
                with r_col2:
                    q_str = str(int(qte)) if isinstance(qte, float) and qte.is_integer() else str(qte)
                    st.markdown(f"**x{q_str}**")
                with r_col3:
                    if st.button("➖", key=f"min_{ing}"):
                        val = float(qte) if isinstance(qte, (int, float)) else 1.0
                        val -= 1
                        if val <= 0:
                            if ing in st.session_state.quantites_custom:
                                del st.session_state.quantites_custom[ing]
                            if ing in st.session_state.articles_perso:
                                st.session_state.articles_perso.remove(ing)
                        else:
                            st.session_state.quantites_custom[ing] = int(val) if val.is_integer() else round(val, 2)
                        st.rerun()
                with r_col4:
                    if st.button("➕", key=f"plus_{ing}"):
                        val = float(qte) if isinstance(qte, (int, float)) else 1.0
                        val += 1
                        st.session_state.quantites_custom[ing] = int(val) if val.is_integer() else round(val, 2)
                        st.rerun()
                with r_col5:
                    if st.button("🗑️", key=f"del_{ing}"):
                        if ing in st.session_state.quantites_custom:
                            del st.session_state.quantites_custom[ing]
                        if ing in st.session_state.articles_perso:
                            st.session_state.articles_perso.remove(ing)
                        to_remove = []
                        for (sh, itm), mult in st.session_state.selections.items():
                            df_s = dataframes[sh]
                            if ing in df_s[df_s.columns[0]].values:
                                to_remove.append((sh, itm))
                        for tr in to_remove:
                            del st.session_state.selections[tr]
                        st.rerun()
                st.markdown("<hr style='margin:5px 0; border:0; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        