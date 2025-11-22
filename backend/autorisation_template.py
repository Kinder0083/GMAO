"""
Template HTML pour générer le PDF d'Autorisation Particulière de Travaux
Format: MAINT_FE_003_V03 - Version compacte (1 page A4)
"""

def generate_autorisation_html(autorisation: dict) -> str:
    """Génère le HTML pour l'autorisation particulière - Version compacte"""
    
    # Données de base
    numero = autorisation.get("numero", "")
    date_etablissement = autorisation.get("date_etablissement", "")
    service_demandeur = autorisation.get("service_demandeur", "")
    responsable = autorisation.get("responsable", "")
    
    # Personnel autorisé - uniquement les entrées remplies
    personnel_autorise = autorisation.get("personnel_autorise", [])
    personnel_rows = ""
    count = 0
    for person in personnel_autorise:
        if person.get("nom") or person.get("fonction"):
            count += 1
            personnel_rows += f"""
                <tr>
                    <td style="border: 1px solid black; padding: 2px 4px; text-align: center;">{count}</td>
                    <td style="border: 1px solid black; padding: 2px 4px;">{person.get('nom', '')}</td>
                    <td style="border: 1px solid black; padding: 2px 4px;">{person.get('fonction', '')}</td>
                </tr>
            """
    
    # Types de travaux - uniquement ceux sélectionnés
    types_travaux = []
    if autorisation.get("type_point_chaud"): types_travaux.append("Par point chaud")
    if autorisation.get("type_fouille"): types_travaux.append("De fouille")
    if autorisation.get("type_espace_clos"): types_travaux.append("En espace clos/confiné")
    if autorisation.get("type_autre_cas"): types_travaux.append("Autre cas")
    
    types_display = " • ".join(types_travaux) if types_travaux else "Non spécifié"
    
    newline = "\n"
    br_tag = "<br>"
    description_travaux = autorisation.get("description_travaux", "")
    
    horaire_debut = autorisation.get("horaire_debut", "")
    horaire_fin = autorisation.get("horaire_fin", "")
    lieu_travaux = autorisation.get("lieu_travaux", "")
    risques_potentiels = autorisation.get("risques_potentiels", "").replace(newline, br_tag)
    
    # Mesures de sécurité - uniquement celles sélectionnées
    mesures_fait = []
    mesures_afaire = []
    
    mesures_map = {
        "mesure_consignation_materiel": "Consignation mat.",
        "mesure_consignation_electrique": "Consignation élec.",
        "mesure_debranchement_force": "Débranch. force",
        "mesure_vidange_appareil": "Vidange app.",
        "mesure_decontamination": "Décontamination",
        "mesure_degazage": "Dégazage",
        "mesure_pose_joint": "Pose joint",
        "mesure_ventilation": "Ventilation",
        "mesure_zone_balisee": "Zone balisée",
        "mesure_canalisations_electriques": "Canal. élec.",
        "mesure_souterraines_balisees": "Souter. balisées",
        "mesure_egouts_cables": "Égouts/câbles",
        "mesure_taux_oxygene": "Taux O2",
        "mesure_taux_explosivite": "Taux explo.",
        "mesure_explosimetre": "Explosimètre",
        "mesure_eclairage_surete": "Éclairage sûreté",
        "mesure_extincteur": "Extincteur",
        "mesure_autres": "Autres"
    }
    
    for key, label in mesures_map.items():
        value = autorisation.get(key, "")
        if value == "FAIT":
            mesures_fait.append(label)
        elif value == "A_FAIRE":
            mesures_afaire.append(label)
    
    mesures_securite_texte = autorisation.get("mesures_securite_texte", "")
    
    # EPI - uniquement ceux sélectionnés
    epi_list = []
    if autorisation.get("epi_visiere"): epi_list.append("Visière")
    if autorisation.get("epi_tenue_impermeable"): epi_list.append("Tenue imperm.")
    if autorisation.get("epi_cagoule_air"): epi_list.append("Cagoule air")
    if autorisation.get("epi_masque"): epi_list.append("Masque")
    if autorisation.get("epi_gant"): epi_list.append("Gants")
    if autorisation.get("epi_harnais"): epi_list.append("Harnais")
    if autorisation.get("epi_outillage_anti_etincelle"): epi_list.append("Out. anti-étincelle")
    if autorisation.get("epi_presence_surveillant"): epi_list.append("Surveillant")
    if autorisation.get("epi_autres"): epi_list.append("Autres")
    
    equipements_protection_texte = autorisation.get("equipements_protection_texte", "")
    
    signature_demandeur = autorisation.get("signature_demandeur", "")
    date_signature_demandeur = autorisation.get("date_signature_demandeur", "")
    signature_responsable_securite = autorisation.get("signature_responsable_securite", "")
    date_signature_responsable = autorisation.get("date_signature_responsable", "")
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Autorisation N°{numero}</title>
    <style>
        @page {{ size: A4; margin: 10mm; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; font-size: 8pt; line-height: 1.2; color: #000; }}
        .container {{ width: 100%; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 4px; margin-bottom: 4px; }}
        .header-right {{ text-align: right; font-size: 7pt; }}
        h1 {{ text-align: center; font-size: 12pt; font-weight: bold; margin: 4px 0; text-transform: uppercase; }}
        .ref-box {{ display: flex; justify-content: space-between; border: 1px solid #000; padding: 3px; background: #f0f0f0; margin-bottom: 4px; font-size: 7pt; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 3px; }}
        th {{ background-color: #e0e0e0; border: 1px solid #000; padding: 2px; font-weight: bold; text-align: left; font-size: 7pt; }}
        td {{ border: 1px solid #000; padding: 2px; font-size: 7pt; }}
        .section-title {{ background-color: #c0c0c0; border: 1px solid #000; padding: 2px 4px; font-weight: bold; margin-top: 3px; font-size: 8pt; }}
        .compact-list {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px; padding: 3px; font-size: 7pt; }}
        .compact-item {{ padding: 1px 3px; }}
        .inline-text {{ padding: 3px; border: 1px solid #ddd; background: #fafafa; font-size: 7pt; margin-top: 2px; }}
        .signature-section {{ display: flex; justify-content: space-between; margin-top: 4px; }}
        .signature-box {{ width: 48%; border: 1px solid #000; padding: 4px; font-size: 7pt; }}
        .signature-title {{ font-weight: bold; margin-bottom: 3px; text-align: center; font-size: 8pt; }}
        .signature-line {{ margin-top: 15px; border-top: 1px solid #000; padding-top: 2px; font-size: 6pt; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- En-tête -->
        <div class="header">
            <div style="width: 80px; height: 40px; border: 1px solid #ccc; display: flex; align-items: center; justify-content: center; font-size: 7pt; color: #666;">LOGO</div>
            <div class="header-right">
                <div><strong>Réf:</strong> MAINT_FE_003</div>
                <div><strong>Rév:</strong> V03</div>
                <div><strong>Date:</strong> {date_etablissement}</div>
            </div>
        </div>

        <h1>AUTORISATION PARTICULIÈRE DE TRAVAUX</h1>

        <div class="ref-box">
            <span>N° AUTORISATION: {numero}</span>
            <span>DATE: {date_etablissement}</span>
        </div>

        <!-- Infos principales -->
        <table>
            <tr><th style="width: 25%;">Service</th><td>{service_demandeur}</td><th style="width: 25%;">Responsable</th><td>{responsable}</td></tr>
        </table>

        <!-- Personnel (si rempli) -->
        {f'''<div class="section-title">PERSONNEL AUTORISÉ</div>
        <table>
            <thead><tr><th style="width: 5%;">N°</th><th>Nom et Prénom</th><th>Fonction</th></tr></thead>
            <tbody>{personnel_rows}</tbody>
        </table>''' if personnel_rows else ''}

        <!-- Type de travaux -->
        <div class="section-title">TYPE DE TRAVAUX</div>
        <div style="padding: 3px; font-size: 7pt;">{types_display}</div>
        {f'<div class="inline-text"><strong>Précisions:</strong> {description_travaux}</div>' if description_travaux else ''}

        <!-- Horaires et lieu -->
        <table style="margin-top: 3px;">
            <tr>
                <th style="width: 15%;">Début</th><td style="width: 15%;">{horaire_debut}</td>
                <th style="width: 15%;">Fin</th><td style="width: 15%;">{horaire_fin}</td>
                <th style="width: 15%;">Lieu</th><td>{lieu_travaux}</td>
            </tr>
        </table>

        <!-- Risques (si rempli) -->
        {f'''<div class="section-title">RISQUES POTENTIELS</div>
        <div class="inline-text">{risques_potentiels}</div>''' if risques_potentiels else ''}

        <!-- Mesures de sécurité (si rempli) -->
        {f'''<div class="section-title">MESURES DE SÉCURITÉ</div>
        {f'<div style="padding: 3px;"><strong style="color: green;">✓ FAIT:</strong> {" • ".join(mesures_fait)}</div>' if mesures_fait else ''}
        {f'<div style="padding: 3px;"><strong style="color: orange;">⚠ À FAIRE:</strong> {" • ".join(mesures_afaire)}</div>' if mesures_afaire else ''}
        {f'<div class="inline-text"><strong>Précisions:</strong> {mesures_securite_texte}</div>' if mesures_securite_texte else ''}''' if mesures_fait or mesures_afaire or mesures_securite_texte else ''}

        <!-- EPI (si rempli) -->
        {f'''<div class="section-title">ÉQUIPEMENTS DE PROTECTION (EPI)</div>
        <div class="compact-list">
            {"".join([f'<div class="compact-item">• {epi}</div>' for epi in epi_list])}
        </div>
        {f'<div class="inline-text"><strong>Précisions:</strong> {equipements_protection_texte}</div>' if equipements_protection_texte else ''}''' if epi_list or equipements_protection_texte else ''}

        <!-- Signatures -->
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-title">DEMANDEUR</div>
                <div><strong>Nom:</strong> {signature_demandeur}</div>
                <div class="signature-line">Date: {date_signature_demandeur}</div>
            </div>
            <div class="signature-box">
                <div class="signature-title">RESPONSABLE SÉCURITÉ</div>
                <div><strong>Nom:</strong> {signature_responsable_securite}</div>
                <div class="signature-line">Date: {date_signature_responsable}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html
