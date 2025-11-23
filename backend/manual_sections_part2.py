# Sections additionnelles du manuel - Partie 2

ADDITIONAL_SECTIONS = {
    # Chapitre 5 : Inventaire
    "sec-005-01": {
        "title": "Ajouter une Pièce à l'Inventaire",
        "content": """📦 **Créer une Nouvelle Pièce**

**Étape 1** : Module "Inventaire"
Cliquez "+ Nouvelle pièce"

**Informations Essentielles**
• **Nom** : Descriptif clair
• **Référence** : Code unique
• **Catégorie** : Électrique, Mécanique, etc.
• **Quantité** : Stock actuel
• **Seuil minimum** : Alerte stock bas
• **Prix unitaire** : Pour calcul des coûts

**Informations Complémentaires**
• Fournisseur principal
• Délai de livraison
• Équipements compatibles
• Emplacement de stockage

**Photo**
Ajoutez une photo pour identification rapide

**Étape 2** : Sauvegarder

✅ **Alerte Automatique**
Si quantité < seuil minimum :
• Badge vert dans le header
• Notification aux responsables

💡 **Astuce Stock**
Définissez le seuil = délai livraison × consommation moyenne""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["inventory"],
        "keywords": ["inventaire", "pièce", "stock", "ajouter"]
    },
    
    "sec-005-02": {
        "title": "Ajuster les Quantités",
        "content": """📊 **Mettre à Jour le Stock**

**3 Façons de Modifier le Stock**

**1. Réception de Commande**
• Module "Inventaire"
• Cliquer sur la pièce
• Bouton "+ Ajouter au stock"
• Quantité reçue
• Commentaire (n° bon livraison)

**2. Correction Manuelle**
• Après un inventaire physique
• Bouton "Ajuster stock"
• Nouvelle quantité
• Motif obligatoire

**3. Utilisation dans un OT**
• Automatique lors de l'ajout de pièces
• Le stock est déduit instantanément
• Traçable dans l'historique

📜 **Historique des Mouvements**
Chaque modification est tracée :
• Date et heure
• Utilisateur
• Quantité avant/après
• Motif

⚠️ **Attention**
Les corrections manuelles doivent être justifiées !

💡 **Inventaire Physique**
Recommandé tous les 6 mois""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["inventory"],
        "keywords": ["stock", "quantité", "ajuster"]
    },
    
    "sec-005-03": {
        "title": "Gérer les Alertes Stock",
        "content": """🔔 **Alertes de Stock Faible**

**Fonctionnement Automatique**
Quand une pièce atteint le seuil minimum :
• Badge VERT dans le header
• Nombre de pièces en alerte
• Liste accessible en un clic

**Voir les Alertes**
1. Cliquer sur le badge vert
2. Redirection vers Inventaire
3. Filtre automatique "Stock faible"

**Actions Possibles**
• Commander la pièce
• Ajuster le seuil
• Trouver une alternative

**Commander**
1. Cliquer sur la pièce
2. Bouton "Commander"
3. Redirige vers "Historique Achat"
4. Créer un bon de commande

**Ajuster le Seuil**
Si alertes trop fréquentes ou rares :
• Modifier le seuil minimum
• Basé sur votre expérience

📊 **Statistiques**
Consultez la consommation moyenne :
• Derniers 30 jours
• Derniers 90 jours
• Tendances

💡 **Conseil**
Commandez avant rupture !""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["inventory"],
        "keywords": ["alerte", "stock faible", "commander"]
    },
    
    # Chapitre 6 : Maintenance Préventive
    "sec-006-01": {
        "title": "Créer un Plan Préventif",
        "content": """🗓️ **Planifier une Maintenance Préventive**

**Qu'est-ce qu'une MP ?**
Intervention planifiée pour :
• Prévenir les pannes
• Prolonger durée de vie
• Respecter les normes

**Étape 1** : Module "Maintenance prev."
Cliquer "+ Nouvelle maintenance"

**Configuration de Base**
• **Équipement** : À maintenir
• **Titre** : Type d'intervention
• **Description** : Tâches à effectuer

**Fréquence**
Choisir le type de récurrence :
• **Calendaire** : Tous les X jours/semaines/mois
• **Au compteur** : Tous les X heures/km/cycles

Exemples :
• Vidange : Tous les 3 mois OU 500 heures
• Graissage : Toutes les 2 semaines
• Contrôle réglementaire : Annuel

**Planning**
• Date de début
• Heure préférée
• Durée estimée
• Technicien assigné

**Checklist**
Créez une liste de tâches :
☑️ Vérifier niveau huile
☑️ Nettoyer filtre
☑️ Contrôler courroie
☑️ Test de fonctionnement

💡 **Conseil**
Basez-vous sur les recommandations du fabricant""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["preventiveMaintenance"],
        "keywords": ["maintenance préventive", "planifier", "MP"]
    },
    
    "sec-006-02": {
        "title": "Exécuter une MP",
        "content": """✅ **Réaliser une Maintenance Préventive**

**Notification Automatique**
Vous êtes notifié :
• Badge ROUGE : MP en retard
• Badge BLEU : MP bientôt due (3 jours avant)

**Étape 1** : Accéder à la MP
• Cliquer sur le badge
• OU Module "Planning M.Prev."
• Sélectionner la MP

**Étape 2** : Démarrer
• Bouton "Commencer"
• Statut passe à "En cours"
• Timer démarre

**Étape 3** : Exécuter la Checklist
Cochez chaque tâche au fur et à mesure :
☑️ Tâche 1
☑️ Tâche 2
☑️ Tâche 3

**Étape 4** : Ajouter Observations
• Anomalies détectées
• Pièces à changer bientôt
• Recommandations

**Étape 5** : Terminer
• Bouton "Terminer la MP"
• Ajouter pièces utilisées si nécessaire
• Temps réel d'intervention

**Étape 6** : Prochaine Occurrence
Automatiquement créée selon la fréquence

💡 **Si Problème Détecté**
Créez un OT correctif depuis la MP""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["preventiveMaintenance"],
        "keywords": ["exécuter", "maintenance", "checklist"]
    },
    
    "sec-006-03": {
        "title": "Planifier les MP au Compteur",
        "content": """⏱️ **Maintenance Basée sur Compteurs**

**Qu'est-ce qu'un Compteur ?**
• Heures de fonctionnement
• Kilomètres parcourus
• Cycles de production
• Nb démarrages

**Créer un Compteur**
1. Module "Compteurs"
2. "+ Nouveau compteur"
3. Associer à un équipement
4. Valeur initiale

**Configurer MP au Compteur**
1. Créer la MP
2. Type : "Au compteur"
3. Fréquence : Ex: "Tous les 500 heures"
4. Compteur : Sélectionner

**Saisir les Relevés**
• Régulièrement (quotidien/hebdo)
• Module "Compteurs"
• Nouvelle valeur
• Date du relevé

**Déclenchement Automatique**
Quand compteur ≥ seuil :
• MP créée automatiquement
• Notification envoyée

💡 **Avantage**
Maintenance basée sur l'utilisation réelle, pas le calendrier""",
        "level": "advanced",
        "target_roles": [],
        "target_modules": ["preventiveMaintenance", "meters"],
        "keywords": ["compteur", "heures", "cycles"]
    },
    
    # Chapitre 7 : Demandes
    "sec-007-01": {
        "title": "Créer une Demande d'Intervention",
        "content": """💬 **Demande d'Intervention**

**Pour Qui ?**
Tous les utilisateurs peuvent créer une demande

**Étape 1** : Module "Demandes d'inter."
Cliquer "+ Nouvelle demande"

**Étape 2** : Décrire le Problème
• **Titre** : Résumé court
• **Description** : Détails
• **Équipement** : Si connu
• **Zone** : Localisation
• **Urgence** : Normal, Urgent

**Étape 3** : Ajouter Détails
• Photo du problème
• Impact sur production
• Date de découverte

**Étape 4** : Soumettre
• La demande est envoyée
• Notification aux techniciens
• N° unique attribué

**Suivi**
• Statut : Nouveau, En cours, Résolu
• Commentaires des techniciens
• Notification quand traité

**Conversion en OT**
Un technicien peut convertir :
• Demande → Ordre de travail
• Si intervention nécessaire

💡 **Quand Utiliser ?**
• Pas d'urgence immédiate
• Besoin d'évaluation
• Petits problèmes""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["interventionRequests"],
        "keywords": ["demande", "intervention", "problème"]
    },
    
    "sec-007-02": {
        "title": "Traiter une Demande",
        "content": """🔍 **Gérer les Demandes Reçues**

⚠️ **Pour** : TECHNICIEN, ADMIN

**Étape 1** : Consulter
Module "Demandes d'inter."
Filtrer par statut "Nouveau"

**Étape 2** : Évaluer
• Lire la description
• Voir les photos
• Comprendre l'urgence

**Étape 3** : Décider
**Option A - Simple** : Résoudre directement
• Ajouter commentaire
• Statut "Résolu"

**Option B - Complexe** : Créer un OT
• Bouton "Convertir en OT"
• Remplir détails OT
• Assigner technicien
• La demande est liée à l'OT

**Étape 4** : Communiquer
Ajoutez un commentaire pour informer le demandeur

💡 **Temps de Réponse**
Objectif : < 2h pour les demandes urgentes""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["interventionRequests"],
        "keywords": ["traiter", "demande", "convertir"]
    },
    
    # Chapitre 8 : QHSE
    "sec-008-01": {
        "title": "Plan de Surveillance",
        "content": """🛡️ **Gérer le Plan de Surveillance**

⚠️ **Pour** : ADMIN, QHSE

**Qu'est-ce que c'est ?**
Surveillance systématique pour :
• Conformité réglementaire
• Sécurité des personnes
• Protection environnement

**Créer un Point de Surveillance**
1. Module "Plan de Surveillance"
2. "+ Nouveau point"
3. Remplir :
   • Équipement/Zone
   • Paramètre surveillé
   • Fréquence de contrôle
   • Valeurs limites (min/max)
   • Responsable

**Effectuer un Relevé**
• Saisir la valeur mesurée
• Date et heure
• Commentaire si anomalie

**Alertes**
Si valeur hors limites :
• Alerte immédiate
• Notification responsable QHSE
• Action corrective à planifier

📊 **Rapports Automatiques**
• Historique des relevés
• Graphiques de tendances
• Conformité règlementaire""",
        "level": "advanced",
        "target_roles": ["ADMIN", "QHSE"],
        "target_modules": ["surveillance"],
        "keywords": ["surveillance", "QHSE", "conformité"]
    },
    
    "sec-008-02": {
        "title": "Gérer les Presqu'accidents",
        "content": """⚠️ **Presqu'accidents et Incidents**

**Importance**
Analyser les presqu'accidents pour :
• Prévenir les accidents graves
• Améliorer la sécurité
• Culture de prévention

**Déclarer un Presqu'accident**
1. Module "Presqu'accident"
2. "+ Nouvelle déclaration"
3. Remplir :
   • Description de la situation
   • Zone concernée
   • Personnes impliquées
   • Gravité potentielle
   • Photos si possible

**Analyse**
• Causes identifiées
• Actions correctives proposées
• Responsable du suivi
• Délai de mise en œuvre

**Suivi des Actions**
• Tableau de bord des actions
• Statut : Planifié, En cours, Réalisé
• Vérification d'efficacité

**Statistiques**
• Nombre de déclarations/mois
• Types de presqu'accidents
• Zones à risque
• Indicateurs de sécurité

💡 **Culture Sécurité**
Encouragez les déclarations sans sanction""",
        "level": "advanced",
        "target_roles": ["ADMIN", "QHSE"],
        "target_modules": ["presquaccident"],
        "keywords": ["presqu'accident", "sécurité", "incident"]
    },
    
    # Chapitre 9 : Rapports
    "sec-009-01": {
        "title": "Générer des Rapports",
        "content": """📊 **Créer des Rapports Personnalisés**

**Types de Rapports Disponibles**

**1. Rapports d'Activité**
• OT par période
• OT par technicien
• OT par équipement
• Temps d'intervention

**2. Rapports Financiers**
• Coûts de maintenance
• Coûts par équipement
• Budget vs Réel
• Historique d'achats

**3. Rapports de Performance**
• Taux de disponibilité
• MTBF / MTTR
• Respect des échéances
• Backlog OT

**Générer un Rapport**
1. Module "Rapports"
2. Sélectionner le type
3. Définir la période
4. Appliquer les filtres
5. Cliquer "Générer"

**Export**
• Format : PDF ou Excel
• Graphiques inclus
• Logo personnalisable

💡 **Rapports Programmés**
Configuration future : envoi automatique par email""",
        "level": "both",
        "target_roles": [],
        "target_modules": ["reports"],
        "keywords": ["rapport", "statistiques", "export"]
    },
    
    "sec-009-02": {
        "title": "Analyser les Performances",
        "content": """📈 **Tableaux de Bord et KPI**

**Indicateurs Clés (KPI)**

**Disponibilité**
= (Temps total - Temps arrêt) / Temps total × 100
Objectif : > 95%

**MTBF** (Mean Time Between Failures)
= Temps total / Nombre de pannes
Plus élevé = Mieux

**MTTR** (Mean Time To Repair)
= Temps total réparation / Nombre OT
Plus bas = Mieux

**Respect des Échéances**
= OT terminés à temps / Total OT × 100
Objectif : > 90%

**Tableau de Bord**
Module "Tableau de bord" :
• Widgets configurables
• Graphiques en temps réel
• Alertes visuelles

**Analyser une Baisse**
1. Identifier la tendance
2. Voir les équipements impactés
3. Consulter les OT associés
4. Prendre action corrective

💡 **Revue Mensuelle**
Organisez une réunion pour analyser les KPI""",
        "level": "advanced",
        "target_roles": [],
        "target_modules": ["reports"],
        "keywords": ["KPI", "performance", "analyse"]
    },
    
    # Chapitre 10 : Personnalisation
    "sec-010-01": {
        "title": "Personnaliser l'Apparence",
        "content": """🎨 **Personnaliser les Couleurs**

**Étape 1** : Module "Personnalisation"
Icône palette 🎨 dans la sidebar

**Onglet Apparence**

**Thèmes Prédéfinis**
• Bleu (par défaut)
• Orange
• Vert
• Blanc (minimaliste)

**Couleurs Personnalisées**
• Couleur primaire : Boutons, liens
• Couleur secondaire : Éléments d'accent
• Couleur sidebar : Fond de la barre latérale

**Aperçu en Temps Réel**
Les changements s'appliquent immédiatement

**Sauvegarder**
Cliquez "Enregistrer" pour conserver

💡 **Conseil**
Utilisez des couleurs contrastées pour la lisibilité""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["personnalisation", "couleurs", "thème"]
    },
    
    "sec-010-02": {
        "title": "Configurer la Sidebar",
        "content": """📐 **Personnaliser la Barre Latérale**

**Options Disponibles**

**Position**
• Gauche (par défaut)
• Droite

**Largeur**
• Compacte : 200px
• Standard : 240px
• Large : 280px

**Comportement**
• Toujours ouverte
• Minimisable (icône ☰)
• Auto-collapse (se ferme automatiquement)

**Organisation du Menu**
Onglet "Organisation du menu" :
• Réorganiser par glisser-déposer
• Masquer les modules inutilisés
• Marquer des favoris ⭐

**Page d'Accueil**
Choisir votre page par défaut après connexion :
• Tableau de bord
• Ordres de travail
• Votre module préféré

💡 **Gain de Temps**
Organisez votre interface selon votre usage quotidien""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["sidebar", "menu", "organisation"]
    },
    
    "sec-010-03": {
        "title": "Widgets du Tableau de Bord",
        "content": """📊 **Personnaliser Votre Dashboard**

**Widgets Disponibles**
☑️ OT en cours
☑️ OT en retard
☑️ MP à venir
☑️ Alertes stock
☑️ Disponibilité équipements
☑️ Coûts du mois
☑️ Temps d'intervention
☑️ Top équipements en panne

**Configurer**
1. Personnalisation → "Tableau de bord"
2. Cocher les widgets désirés
3. Enregistrer

**Disposition**
Les widgets s'affichent en grille responsive

**Actualisation**
Données mises à jour en temps réel

💡 **Conseil par Rôle**
• DIRECTEUR : KPI et coûts
• TECHNICIEN : OT assignés
• QHSE : Plan surveillance et incidents""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["dashboard", "widgets", "tableau de bord"]
    },
    
    # Chapitre 11 : FAQ
    "sec-011-01": {
        "title": "Problèmes de Connexion",
        "content": """🔐 **FAQ : Connexion**

**Q : J'ai oublié mon mot de passe**
R : Cliquez sur "Mot de passe oublié" → Email de réinitialisation

**Q : Mon compte est bloqué**
R : Après 5 tentatives échouées, contactez l'admin

**Q : L'application ne charge pas**
R : Vérifiez votre connexion internet, videz le cache (Ctrl+Shift+R)

**Q : Je suis déconnecté automatiquement**
R : Session expire après 8h d'inactivité (sécurité)

**Q : Mes permissions ont changé**
R : Normal si l'admin a modifié votre rôle

💡 **Support**
Bouton "Aide" en haut → Demande envoyée aux admins""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["connexion", "mot de passe", "bloqué", "FAQ"]
    },
    
    "sec-011-02": {
        "title": "Problèmes avec les OT",
        "content": """📋 **FAQ : Ordres de Travail**

**Q : Je ne peux pas créer d'OT**
R : Vérifiez vos permissions (module workOrders > edit)

**Q : L'équipement n'apparaît pas dans la liste**
R : L'équipement existe ? Statut pas \"Déclassé\" ?

**Q : Je ne peux pas joindre de fichier**
R : Taille max 10 Mo, format accepté : JPG, PNG, PDF

**Q : L'OT a disparu**
R : Filtres actifs ? Vérifié dans "Tous" ?

**Q : Stock non déduit après ajout pièce**
R : Actualisez la page, vérifiez l'inventaire

**Q : Impossible de fermer l'OT**
R : Permission "edit" requise, tous les champs remplis ?

💡 **Astuce**
Utilisez la recherche globale (Ctrl+K) pour trouver un OT""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["FAQ", "problème", "ordre travail"]
    },
    
    "sec-011-03": {
        "title": "Problèmes de Performance",
        "content": """⚡ **FAQ : Performance et Lenteurs**

**Q : L'application est lente**
R : 
1. Videz le cache navigateur
2. Fermez les onglets inutiles
3. Vérifiez votre connexion internet

**Q : Les tableaux mettent du temps à charger**
R : Normal si +1000 lignes. Utilisez les filtres par date

**Q : L'upload de fichier échoue**
R : Fichier trop volumineux ? Compressez les images

**Q : Les graphiques ne s'affichent pas**
R : Désactivez les bloqueurs de pub (AdBlock)

**Q : Notifications en retard**
R : Actualisez la page, les notifications sont en temps réel

💡 **Optimisation**
• Filtrez vos données
• Fermez les modales inutilisées
• Utilisez Chrome ou Firefox (recommandé)""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["performance", "lenteur", "optimisation"]
    }
}
"}]