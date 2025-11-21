"""
Template HTML pour la génération du PDF Bon de Travail
Format: MAINT_FE_004_V02 - Basé EXACTEMENT sur le document Word officiel
"""

def generate_bon_travail_html(bon):
    """
    Génère le HTML du bon de travail selon le format EXACT du document Word MAINT_FE_004_V02
    """
    
    # Extraction des données
    date_engagement = bon.get('date_engagement', '')[:10] if bon.get('date_engagement') else ''
    
    # Fonction helper pour générer les checkboxes
    def checkbox(label, checked_list, value):
        checked = value in (checked_list or [])
        check_mark = '✓' if checked else ''
        return f'<div class="checkbox-item"><span class="checkbox {"checked" if checked else ""}">{check_mark}</span><span class="checkbox-label">{label}</span></div>'
    
    # Listes selon le document Word EXACT
    risques_materiel_list = [
        'Non décontaminé ou en charge avec des produits',
        'Sous pression',
        'Alimenté (électricité, air comprimé,…)',
        'Présentant des pièces en mouvements',
        'En hauteur (> 2 m)'
    ]
    
    risques_autorisation_list = ['Point chaud', 'Espace confiné']
    
    risques_produits_list = [
        'Pour l\'homme (Toxique, Corrosif, Irritant, ou sensibilisant)',
        'Pour l\'homme ou le matériel (inflammable, explosif)',
        'Pour l\'environnement'
    ]
    
    risques_environnement_list = [
        'Co-activité avec du personnel d\'IRIS ou d\'autres entreprises intervenantes',
        'Passage de chariot à proximité',
        'Tuyauterie ou ligne électrique à proximité',
        'Poussières sensibles à l\'explosion'
    ]
    
    precautions_materiel_list = [
        'Vidange / lavage / décontamination préalable',
        'Pose d\'un joint plein',
        'Consignation électrique et/ou mécanique',
        'Utilisation d\'un échafaudage',
        'Utilisation d\'un chariot ou d\'une nacelle'
    ]
    
    precautions_hommes_list = [
        'Lunettes ou visière adaptée',
        'Gants adaptés',
        'Combinaison',
        'Masque à gaz ou à poussière'
    ]
    
    precautions_environnement_list = [
        'Balisage de la zone de travaux',
        'Extincteurs adaptés ou RIA à proximité'
    ]
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bon de travail - MAINT_FE_004_V02</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
        }}
        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            font-size: 11pt;
            line-height: 1.5;
            color: #000;
        }}
        
        /* Titre principal */
        h1 {{
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            margin: 10px 0 20px 0;
            text-decoration: underline;
        }}
        
        /* Paragraphe d'introduction */
        .intro {{
            text-align: justify;
            font-size: 10pt;
            line-height: 1.4;
            margin-bottom: 20px;
            padding: 8px;
            border: 1px solid #ccc;
            background-color: #f9f9f9;
        }}
        
        /* Sections */
        .section {{
            margin: 15px 0;
        }}
        
        .section-title {{
            font-weight: bold;
            font-size: 11pt;
            text-decoration: underline;
            margin: 15px 0 10px 0;
        }}
        
        .subsection-title {{
            font-weight: bold;
            font-size: 10pt;
            margin: 10px 0 5px 0;
        }}
        
        /* Champs de formulaire */
        .form-field {{
            margin: 8px 0;
            padding: 3px 0;
        }}
        
        .form-field strong {{
            font-weight: bold;
        }}
        
        .form-value {{
            display: inline-block;
            min-width: 200px;
            border-bottom: 1px solid #000;
            padding: 2px 5px;
        }}
        
        /* Checkboxes */
        .checkbox-group {{
            margin: 8px 0;
        }}
        
        .checkbox-item {{
            margin: 4px 0;
            padding-left: 10px;
            display: flex;
            align-items: center;
        }}
        
        .checkbox {{
            display: inline-block;
            width: 15px;
            height: 15px;
            border: 2px solid #000;
            margin-right: 8px;
            text-align: center;
            line-height: 13px;
            font-size: 12px;
            font-weight: bold;
            flex-shrink: 0;
        }}
        
        .checkbox.checked {{
            background-color: #000;
            color: white;
        }}
        
        .checkbox-label {{
            flex: 1;
        }}
        
        /* Avertissement */
        .warning {{
            margin: 10px 0;
            padding: 8px;
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            font-size: 10pt;
        }}
        
        .warning strong {{
            font-weight: bold;
        }}
        
        /* Tableau Zone Inflammable */
        .zone-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        
        .zone-table td {{
            border: 2px solid #000;
            padding: 10px;
            height: 40px;
        }}
        
        .zone-table .label-cell {{
            font-weight: bold;
            width: 30%;
            background-color: #e0e0e0;
        }}
        
        /* Section Engagement */
        .engagement {{
            margin: 20px 0;
            padding: 10px;
            border: 2px solid #000;
            text-align: justify;
        }}
        
        .engagement-title {{
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 8px;
        }}
        
        /* Table des signatures */
        .signature-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .signature-table th {{
            border: 2px solid #000;
            padding: 8px;
            background-color: #d0d0d0;
            font-weight: bold;
            text-align: center;
            font-size: 10pt;
        }}
        
        .signature-table td {{
            border: 2px solid #000;
            padding: 15px;
            height: 80px;
            vertical-align: top;
            text-align: center;
        }}
        
        /* Pied de page */
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #000;
            font-size: 9pt;
            font-style: italic;
            text-align: center;
        }}
        
        @media print {{
            body {{ margin: 0; }}
        }}
    </style>
</head>
<body>
    <!-- TITRE PRINCIPAL -->
    <h1>Bon de travail</h1>
    
    <!-- PARAGRAPHE D'INTRODUCTION -->
    <div class="intro">
        Le bon de travail, permet d'identifier les risques liés aux travaux spécifiés ci-dessous ainsi que les précautions à prendre pour éviter tout accident, dégât matériel ou atteinte à l'environnement. Ce bon de travail tient lieu de plan de prévention. Sauf contre-indication particulière (ou modification des conditions d'intervention), le bon de travail est valable pour toute la durée du chantier (dans la limite de 24 heures).
    </div>
    
    <!-- SECTION 1: TRAVAUX À RÉALISER -->
    <div class="section">
        <div class="section-title">Travaux à réaliser</div>
        <div class="form-field">
            <strong>Localisation / Ligne :</strong> <span class="form-value">{bon.get('localisation_ligne', '')}</span>
        </div>
        <div class="form-field">
            <strong>Description :</strong> <span class="form-value">{bon.get('description_travaux', '')}</span>
        </div>
        <div class="form-field">
            <strong>Nom des intervenants :</strong> <span class="form-value">{bon.get('nom_intervenants', '')}</span>
        </div>
    </div>
    
    <!-- SECTION 2: RISQUES IDENTIFIÉS -->
    <div class="section">
        <div class="section-title">Risques Identifiés</div>
        
        <div class="subsection-title">Intervention sur du matériel ou des infrastructures :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('risques_materiel', []), label) for label in risques_materiel_list])}
            <div class="checkbox-item">
                <span class="checkbox"></span>
                <span class="checkbox-label">Autre (préciser) : {bon.get('risques_materiel_autre', '')}</span>
            </div>
        </div>
        
        <div class="subsection-title">Travaux nécessitant une autorisation particulière :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('risques_autorisation', []), label) for label in risques_autorisation_list])}
        </div>
        
        <div class="subsection-title">Produits dangereux :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('risques_produits', []), label) for label in risques_produits_list])}
        </div>
        
        <div class="subsection-title">Environnement des travaux nécessitant une attention particulière :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('risques_environnement', []), label) for label in risques_environnement_list])}
            <div class="checkbox-item">
                <span class="checkbox"></span>
                <span class="checkbox-label">Autre (préciser) : {bon.get('risques_environnement_autre', '')}</span>
            </div>
        </div>
    </div>
    
    <!-- SECTION 3: PRÉCAUTIONS À PRENDRE -->
    <div class="section">
        <div class="section-title">Précautions à Prendre</div>
        
        <div class="subsection-title">Sur le matériel ou les infrastructures :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('precautions_materiel', []), label) for label in precautions_materiel_list])}
            <div class="checkbox-item">
                <span class="checkbox"></span>
                <span class="checkbox-label">Autre (préciser) : {bon.get('precautions_materiel_autre', '')}</span>
            </div>
        </div>
        
        <div class="warning">
            <strong>Avertissement :</strong> L'utilisation d'un chariot ou d'une nacelle n'est possible qu'après que l'entreprise intervenante ait fourni à IRIS une autorisation nominative de conduite.
        </div>
        
        <div class="subsection-title">Sur les hommes, le matériel ou l'environnement :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('precautions_epi', []), label) for label in precautions_hommes_list])}
            <div class="checkbox-item">
                <span class="checkbox"></span>
                <span class="checkbox-label">Autre (préciser) : {bon.get('precautions_epi_autre', '')}</span>
            </div>
        </div>
        
        <div class="subsection-title">Sur l'environnement des travaux :</div>
        <div class="checkbox-group">
            {''.join([checkbox(label, bon.get('precautions_environnement', []), label) for label in precautions_environnement_list])}
            <div class="checkbox-item">
                <span class="checkbox"></span>
                <span class="checkbox-label">Autre (préciser) : {bon.get('precautions_environnement_autre', '')}</span>
            </div>
        </div>
        
        <!-- TABLEAU ZONE INFLAMMABLE -->
        <table class="zone-table">
            <tr>
                <td class="label-cell">Zone Inflammable</td>
                <td>{bon.get('zone_inflammable', '')}</td>
            </tr>
        </table>
    </div>
    
    <!-- SECTION 4: ENGAGEMENT -->
    <div class="engagement">
        <div class="engagement-title">Engagement</div>
        <p>Le représentant de l'entreprise intervenante reconnaît avoir pris connaissance des risques liés aux travaux qui lui sont confiés et s'engage à appliquer et faire appliquer les mesures de précaution qui lui ont été notifiées.</p>
    </div>
    
    <!-- TABLE DES SIGNATURES -->
    <table class="signature-table">
        <tr>
            <th>Date</th>
            <th>Nom et visa du demandeur</th>
            <th>Nom et visa du représentant de l'intervenant</th>
        </tr>
        <tr>
            <td>{date_engagement}</td>
            <td>{bon.get('nom_agent_maitrise', '')}</td>
            <td>{bon.get('nom_representant', '')}</td>
        </tr>
    </table>
    
    <!-- PIED DE PAGE -->
    <div class="footer">
        Remettre une copie à l'intervenant – Archivage Direction du site
    </div>
</body>
</html>
    """
    
    return html_content
