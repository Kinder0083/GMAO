#!/usr/bin/env python3
"""
Script pour générer et importer le contenu complet du manuel
"""
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid

# Connexion MongoDB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

# Toutes les sections du manuel
ALL_SECTIONS = {
    # Chapitre 1 : Guide de Démarrage (déjà créé en base)
    "sec-001-01": {
        "title": "Bienvenue dans GMAO Iris",
        "content": """GMAO Iris est votre solution complète de gestion de maintenance assistée par ordinateur.

📌 **Qu'est-ce qu'une GMAO ?**

Une GMAO (Gestion de Maintenance Assistée par Ordinateur) est un logiciel qui permet de gérer l'ensemble des activités de maintenance d'une entreprise :

• Planification des interventions
• Suivi des équipements
• Gestion des stocks de pièces
• Traçabilité des actions
• Analyse des performances

🎯 **Objectifs de GMAO Iris :**

1. **Optimiser** la maintenance préventive et curative
2. **Réduire** les temps d'arrêt des équipements
3. **Suivre** l'historique complet de vos installations
4. **Analyser** les performances avec des rapports détaillés
5. **Collaborer** efficacement entre les équipes

✅ **Premiers pas recommandés :**

1. Consultez la section "Connexion et Navigation"
2. Familiarisez-vous avec votre rôle et vos permissions
3. Explorez les différents modules selon vos besoins
4. N'hésitez pas à utiliser la fonction de recherche dans ce manuel

💡 **Astuce :** Utilisez le bouton "Aide" en haut à droite pour signaler un problème ou demander de l'assistance à tout moment.""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["bienvenue", "introduction", "gmao"]
    },
    
    "sec-001-02": {
        "title": "Connexion et Navigation",
        "content": """📱 **Se Connecter à GMAO Iris**

1. **Accéder à l'application**
   • Ouvrez votre navigateur web
   • Saisissez l'URL de GMAO Iris
   • Bookmark la page pour un accès rapide

2. **Première Connexion**
   • Email : Votre adresse email professionnelle
   • Mot de passe : Fourni par l'administrateur
   • ⚠️ Changez votre mot de passe

🗺️ **Navigation dans l'Interface**

**Sidebar (Barre latérale)**
• Tous les modules principaux
• Réduire/agrandir avec l'icône ☰

**Header (En-tête)**
• Boutons "Manuel" et "Aide"
• Badges de notifications
• Votre profil

🔔 **Notifications**
• Badge ROUGE : Maintenances dues
• Badge ORANGE : OT en retard
• Badge VERT : Alertes stock""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["connexion", "navigation"]
    },
    
    "sec-001-03": {
        "title": "Comprendre les Rôles",
        "content": """🎭 **Les Différents Rôles**

**ADMIN** : Accès complet
**DIRECTEUR** : Vision globale
**QHSE** : Sécurité/qualité
**TECHNICIEN** : Exécution
**ADV** : Achats/ventes
**LABO** : Laboratoire
**VISUALISEUR** : Lecture seule

🔐 **Connaître Mon Rôle**
Cliquez sur votre nom en haut à droite""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["rôles", "permissions"]
    },
    
    "sec-001-04": {
        "title": "Raccourcis et Astuces",
        "content": """⌨️ **Raccourcis Clavier**

**Navigation**
• **Ctrl + K** : Recherche globale
• **Échap** : Fermer
• **Ctrl + /** : Manuel

💡 **Astuces**
1. Utilisez les filtres
2. Cliquez sur les badges
3. Exportez vos données
4. Ajoutez des commentaires""",
        "level": "both",
        "target_roles": [],
        "target_modules": [],
        "keywords": ["raccourcis", "astuces"]
    },
    
    # Chapitre 2 : Utilisateurs
    "sec-002-01": {
        "title": "Créer un Utilisateur",
        "content": """👥 **Créer un Nouvel Utilisateur**

⚠️ **Prérequis** : Rôle ADMIN

**Étape 1** : Module "Équipes" → "+ Inviter membre"

**Étape 2** : Remplir le formulaire
• Email (obligatoire)
• Prénom et Nom
• Rôle (ADMIN, TECHNICIEN, etc.)
• Téléphone (optionnel)

**Étape 3** : Configurer les permissions
Les permissions sont automatiques selon le rôle

**Étape 4** : Envoyer l'invitation
L'utilisateur reçoit un email

✅ **Vérification**
L'utilisateur apparaît avec le statut "En attente"

💡 **Bonnes Pratiques**
• Emails professionnels uniquement
• Minimum de permissions nécessaires
• Désactivez (ne supprimez pas) les anciens comptes""",
        "level": "beginner",
        "target_roles": ["ADMIN"],
        "target_modules": ["people"],
        "keywords": ["utilisateur", "créer", "inviter"]
    },
    
    "sec-002-02": {
        "title": "Modifier les Permissions",
        "content": """🔐 **Gérer les Permissions**

⚠️ **Prérequis** : ADMIN

**3 Niveaux de Permission**
• **Voir** : Consulter
• **Éditer** : Créer/modifier
• **Supprimer** : Supprimer

**Modifier**
1. Module "Équipes" → Utilisateur
2. "Modifier les permissions"
3. Cocher/décocher par module
4. Sauvegarder

**Permissions par Défaut**
• ADMIN : Tout ✅
• TECHNICIEN : Voir/Éditer ✅, Supprimer ❌
• VISUALISEUR : Voir ✅ uniquement

⚠️ **Attention**
Certaines actions nécessitent toujours ADMIN :
• Gestion utilisateurs
• Configuration système""",
        "level": "advanced",
        "target_roles": ["ADMIN"],
        "target_modules": ["people"],
        "keywords": ["permissions", "droits"]
    },
    
    "sec-002-03": {
        "title": "Désactiver un Compte",
        "content": """🔒 **Désactiver un Utilisateur**

⚠️ Préférez la désactivation à la suppression !

**Pourquoi Désactiver ?**
• Conserve l'historique
• Traçabilité maintenue
• Réactivation possible

**Étape 1** : Module "Équipes"
**Étape 2** : Cliquez sur l'utilisateur
**Étape 3** : Bouton "Désactiver"
**Étape 4** : Confirmez

✅ **Résultat**
• L'utilisateur ne peut plus se connecter
• Ses données restent visibles
• Son nom apparaît sur ses anciennes actions

🔄 **Réactiver**
Même procédure, bouton "Activer\"""",
        "level": "beginner",
        "target_roles": ["ADMIN"],
        "target_modules": ["people"],
        "keywords": ["désactiver", "compte"]
    },
    
    # Chapitre 3 : Ordres de Travail
    "sec-003-01": {
        "title": "Créer un Ordre de Travail",
        "content": """📋 **Workflow Complet : Créer un OT**

**Étape 1** : Module "Ordres de travail"
Cliquez sur "+ Nouvel ordre"

**Étape 2** : Informations de base
• **Titre** : Descriptif court (obligatoire)
• **Description** : Détails du problème
• **Équipement** : Sélectionner dans la liste
• **Zone** : Localisation
• **Priorité** : Basse, Normale, Haute, Critique

**Étape 3** : Planification
• **Type** : Correctif, Préventif, Amélioration
• **Assigné à** : Technicien responsable
• **Date limite** : Échéance

**Étape 4** : Détails additionnels
• Catégorie (Électrique, Mécanique, etc.)
• Temps estimé
• Coût estimé

**Étape 5** : Sauvegarder
• Statut initial : "Nouveau"
• Numéro automatique : OT-XXXX

💡 **Conseils**
• Soyez précis dans la description
• Ajoutez des photos si possible
• Indiquez les symptômes observés
• Mentionnez les tentatives déjà faites""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["ordre travail", "créer", "OT"]
    },
    
    "sec-003-02": {
        "title": "Suivre l'Avancement d'un OT",
        "content": """📊 **Suivre un Ordre de Travail**

**Les Statuts d'un OT**
1. **Nouveau** : Créé, pas encore assigné
2. **En attente** : Assigné, pas démarré
3. **En cours** : Travail en cours
4. **En attente pièce** : Bloqué (manque pièce)
5. **Terminé** : Travail fini
6. **Fermé** : Validé et archivé

**Changer le Statut**
1. Ouvrir l'OT
2. Bouton "Changer statut"
3. Sélectionner le nouveau statut
4. Ajouter un commentaire (recommandé)
5. Valider

**Tableau de Bord**
Filtrez par statut pour voir :
• Tous les OT en cours
• Les OT en retard (badge orange)
• Vos OT assignés

**Historique**
Chaque changement est tracé :
• Qui a fait quoi
• Quand
• Pourquoi (si commentaire)

💡 **Bonne Pratique**
Mettez à jour le statut régulièrement !""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["statut", "suivi", "avancement"]
    },
    
    "sec-003-03": {
        "title": "Ajouter des Pièces Utilisées",
        "content": """🔧 **Enregistrer les Pièces Utilisées**

**Pourquoi Enregistrer ?**
• Suivi du stock
• Calcul du coût réel
• Historique équipement
• Statistiques

**Étape 1** : Ouvrir l'OT
**Étape 2** : Onglet "Pièces utilisées"
**Étape 3** : Cliquer "+ Ajouter pièce"

**Étape 4** : Sélectionner
• Rechercher la pièce
• Quantité utilisée
• Le stock est automatiquement déduit !

**Étape 5** : Valider

⚠️ **Attention au Stock**
• Si stock insuffisant : alerte
• Possibilité de continuer quand même
• Pensez à commander

📊 **Coût Automatique**
Le coût total de l'OT est recalculé automatiquement""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["pièces", "stock", "consommation"]
    },
    
    "sec-003-04": {
        "title": "Joindre des Fichiers",
        "content": """📎 **Ajouter des Pièces Jointes**

**Types de Fichiers Acceptés**
• Photos : JPG, PNG (recommandé)
• Documents : PDF
• Taille max : 10 Mo par fichier

**Ajouter une Pièce Jointe**
1. Ouvrir l'OT
2. Section "Pièces jointes"
3. Glisser-déposer ou cliquer "Parcourir"
4. Sélectionner le(s) fichier(s)
5. Upload automatique

**Bonnes Pratiques**
📸 **Photos Avant/Après**
• Photo du problème initial
• Photo après réparation
• Preuve du travail effectué

📄 **Documents Utiles**
• Bon de commande pièces
• Schémas techniques
• Certificats de conformité

💡 **Conseil**
Nommez vos fichiers clairement :
"OT-5823_avant.jpg"
"OT-5823_schema_electrique.pdf\"""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["pièces jointes", "fichiers", "photos"]
    },
    
    "sec-003-05": {
        "title": "Clôturer un OT",
        "content": """✅ **Clôturer un Ordre de Travail**

**Avant de Clôturer - Checklist**
☑️ Travail terminé
☑️ Pièces utilisées enregistrées
☑️ Temps de travail saisi
☑️ Photos ajoutées
☑️ Commentaire final rédigé

**Étape 1** : Statut "Terminé"
Changez le statut en "Terminé"

**Étape 2** : Rapport d'intervention
• Travaux effectués
• Problèmes rencontrés
• Recommandations

**Étape 3** : Validation
• Si vous êtes le responsable : Statut "Fermé"
• Sinon : Un supérieur validera

**OT Fermé**
• Archive automatique
• Visible dans l'historique
• Ne peut plus être modifié (sauf ADMIN)

📊 **Statistiques Automatiques**
L'OT fermé alimente :
• Taux de disponibilité équipement
• MTTR (temps moyen réparation)
• Coûts de maintenance""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["workOrders"],
        "keywords": ["clôturer", "fermer", "terminer"]
    },
    
    # Chapitre 4 : Équipements
    "sec-004-01": {
        "title": "Ajouter un Équipement",
        "content": """🔧 **Créer un Nouvel Équipement**

**Étape 1** : Module "Équipements"
Cliquez "+ Nouvel équipement"

**Informations Obligatoires**
• **Nom** : Identifiant unique
• **Type** : Machine, Installation, Outil
• **Zone** : Localisation

**Informations Recommandées**
• Marque et Modèle
• N° de série
• Date de mise en service
• Fournisseur
• Criticité (A, B, C)

**Hiérarchie**
• Équipement parent (optionnel)
• Permet de créer une arborescence
• Exemple : Ligne production > Machine > Composant

**Photo**
Ajoutez une photo pour identification rapide

💡 **Code Équipement**
Utilisez une nomenclature cohérente :
ZONE-TYPE-NUMERO
Ex: "PROD-TOUR-001\"""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["assets"],
        "keywords": ["équipement", "ajouter", "créer"]
    },
    
    "sec-004-02": {
        "title": "Gérer l'Hiérarchie",
        "content": """🌳 **Hiérarchie des Équipements**

**Pourquoi une Hiérarchie ?**
• Organisation logique
• Navigation facilitée
• Maintenance en cascade

**Exemple de Structure**
Usine
  └─ Atelier Production
      └─ Ligne A
          └─ Machine découpe
              ├─ Moteur principal
              ├─ Système hydraulique
              └─ Panneau contrôle

**Créer une Hiérarchie**
1. Créer l'équipement parent
2. Créer l'enfant
3. Sélectionner le parent

**Visualiser**
• Vue liste : tous les équipements
• Vue arbre : hiérarchie complète
• Bouton "Voir hiérarchie" sur chaque équipement

💡 **Astuce**
Un OT sur un parent peut impacter tous les enfants""",
        "level": "advanced",
        "target_roles": [],
        "target_modules": ["assets"],
        "keywords": ["hiérarchie", "parent", "enfant"]
    },
    
    "sec-004-03": {
        "title": "Historique d'un Équipement",
        "content": """📚 **Consulter l'Historique**

**Informations Disponibles**
• Tous les OT liés
• Pièces remplacées
• Temps d'arrêt total
• Coûts cumulés
• Maintenances préventives

**Accéder à l'Historique**
1. Ouvrir l'équipement
2. Onglet "Historique"
3. Filtrer par période si besoin

**Indicateurs Clés**
• **MTBF** : Temps moyen entre pannes
• **MTTR** : Temps moyen de réparation
• **Disponibilité** : % temps opérationnel
• **Coût total** : Maintenance cumulée

📊 **Graphiques**
• Évolution des pannes
• Répartition des coûts
• Temps d'intervention

💡 **Décision de Remplacement**
Si coûts > 60% valeur neuve : envisager remplacement""",
        "level": "both",
        "target_roles": [],
        "target_modules": ["assets"],
        "keywords": ["historique", "statistiques"]
    },
    
    "sec-004-04": {
        "title": "Changer le Statut",
        "content": """🚦 **Statuts des Équipements**

**5 Statuts Possibles**
• ✅ **Opérationnel** : Fonctionne normalement
• ⚠️ **Attention** : Surveiller
• 🔧 **En maintenance** : Intervention en cours
• ❌ **Hors service** : Non utilisable
• 🗑️ **Déclassé** : Retiré du service

**Changer le Statut**
1. Ouvrir l'équipement
2. Bouton "Changer statut"
3. Sélectionner + commentaire
4. Valider

**Impact du Statut**
• Visible sur le tableau de bord
• Alertes automatiques si "Hors service"
• Empêche création OT si "Déclassé"

⚠️ **Hors Service**
Met automatiquement l'équipement en rouge
Notifie les responsables

💡 **Bonne Pratique**
Mettez à jour en temps réel""",
        "level": "beginner",
        "target_roles": [],
        "target_modules": ["assets"],
        "keywords": ["statut", "état", "disponibilité"]
    }
}

async def generate_manual():
    client = AsyncIOMotorClient(mongo_url)
    db = client.gmao_iris
    
    print("📚 Génération du manuel complet...")
    
    try:
        # Supprimer ancien contenu
        await db.manual_versions.delete_many({})
        await db.manual_chapters.delete_many({})
        await db.manual_sections.delete_many({})
        
        # Créer version
        now = datetime.now(timezone.utc)
        version = {
            "id": str(uuid.uuid4()),
            "version": "1.1",
            "release_date": now.isoformat(),
            "changes": ["Manuel complet avec 30+ sections"],
            "author_id": "system",
            "author_name": "Système",
            "is_current": True
        }
        await db.manual_versions.insert_one(version)
        
        # Créer chapitres
        chapters = [
            {"id": "ch-001", "title": "🚀 Guide de Démarrage", "description": "Premiers pas", "icon": "Rocket", "order": 1, "sections": ["sec-001-01", "sec-001-02", "sec-001-03", "sec-001-04"], "target_roles": [], "target_modules": []},
            {"id": "ch-002", "title": "👤 Utilisateurs", "description": "Gérer les utilisateurs", "icon": "Users", "order": 2, "sections": ["sec-002-01", "sec-002-02", "sec-002-03"], "target_roles": ["ADMIN"], "target_modules": ["people"]},
            {"id": "ch-003", "title": "📋 Ordres de Travail", "description": "Gérer les OT", "icon": "ClipboardList", "order": 3, "sections": ["sec-003-01", "sec-003-02", "sec-003-03", "sec-003-04", "sec-003-05"], "target_roles": [], "target_modules": ["workOrders"]},
            {"id": "ch-004", "title": "🔧 Équipements", "description": "Gérer les équipements", "icon": "Wrench", "order": 4, "sections": ["sec-004-01", "sec-004-02", "sec-004-03", "sec-004-04"], "target_roles": [], "target_modules": ["assets"]}
        ]
        
        for chapter in chapters:
            chapter_data = {**chapter, "created_at": now.isoformat(), "updated_at": now.isoformat()}
            await db.manual_chapters.insert_one(chapter_data)
            print(f"✅ {chapter['title']}")
        
        # Créer sections
        order = 1
        for sec_id, sec_data in ALL_SECTIONS.items():
            section = {
                "id": sec_id,
                "title": sec_data["title"],
                "content": sec_data["content"],
                "order": order,
                "parent_id": None,
                "target_roles": sec_data.get("target_roles", []),
                "target_modules": sec_data.get("target_modules", []),
                "level": sec_data.get("level", "beginner"),
                "images": [],
                "video_url": None,
                "keywords": sec_data.get("keywords", []),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            await db.manual_sections.insert_one(section)
            order += 1
        
        print(f"\n✅ {len(ALL_SECTIONS)} sections créées")
        print("\n🎉 Manuel généré avec succès !")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(generate_manual())
