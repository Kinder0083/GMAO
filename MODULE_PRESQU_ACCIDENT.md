# Module Presqu'accident (Near Miss) - Documentation

## Vue d'ensemble
Module complet de gestion des presqu'accidents (incidents évités de justesse) intégré dans l'application GMAO Atlas.

**Version:** 1.6.0  
**Date de création:** Novembre 2025  
**Pattern utilisé:** Similaire au module "Plan de Surveillance"

---

## Structure du module

### Backend (`/app/backend`)

#### Fichiers créés/modifiés:

1. **`models.py`** - Modèles de données
   - `PresquAccidentStatus` (Enum): A_TRAITER, EN_COURS, TERMINE, ARCHIVE
   - `PresquAccidentService` (Enum): ADV, LOGISTIQUE, PRODUCTION, QHSE, MAINTENANCE, LABO, INDUS, AUTRE
   - `PresquAccidentSeverity` (Enum): FAIBLE, MOYEN, ELEVE, CRITIQUE
   - `PresquAccidentItem` (Model): Modèle complet avec tous les champs
   - `PresquAccidentItemCreate` (Model): Pour la création
   - `PresquAccidentItemUpdate` (Model): Pour les mises à jour
   - Ajout de `presquaccident` dans `UserPermissions`
   - Ajout de `PRESQU_ACCIDENT` dans `EntityType`

2. **`presqu_accident_routes.py`** - Routes API complètes
   - CRUD complet (GET, POST, PUT, DELETE)
   - Statistiques (stats, rapport-stats, badge-stats)
   - Alertes (items à traiter, en retard)
   - Upload de pièces jointes
   - Import/Export CSV

3. **`server.py`** - Intégration du module
   - Import et initialisation des routes
   - Ajout dans EXPORT_MODULES: `"presqu-accident-items": "presqu_accident_items"`
   - Column mappings pour l'import

4. **`migrations/add_presqu_accident_permissions.py`** - Migration DB
   - Ajout automatique des permissions presquaccident aux utilisateurs existants

---

### Frontend (`/app/frontend/src`)

#### Fichiers créés:

1. **`pages/PresquAccidentList.jsx`** - Page principale
   - Liste complète avec filtres (service, statut, sévérité, recherche)
   - Formulaire modal de création/édition
   - Cartes statistiques (Total, À traiter, En cours, Terminés)
   - Actions: Créer, Modifier, Supprimer

2. **`pages/PresquAccidentRapport.jsx`** - Page de rapport KPIs
   - 3 modes d'affichage: Cards, Table, Charts
   - Statistiques globales (taux traitement, retards, délai moyen)
   - Graphiques par service, sévérité, lieu
   - Utilise @nivo/pie et @nivo/bar

#### Fichiers modifiés:

1. **`services/api.js`** - API client
   - Export `presquAccidentAPI` avec toutes les méthodes
   - CRUD, stats, alertes, upload, import/export

2. **`App.js`** - Routes
   - `/presqu-accident` → PresquAccidentList
   - `/presqu-accident-rapport` → PresquAccidentRapport

3. **`components/Layout/MainLayout.jsx`** - Navigation
   - Ajout des 2 liens de menu
   - Import de `AlertTriangle` icon

4. **`components/Common/PermissionsGrid.jsx`** - Permissions
   - Ajout de la ligne "Presqu'accident"

5. **`pages/ImportExport.jsx`** - Import/Export
   - Ajout dans la liste des modules exportables

---

## Endpoints API

Base URL: `/api/presqu-accident`

### CRUD
- `GET /items` - Liste avec filtres (service, status, severite, lieu)
- `GET /items/{id}` - Détails d'un item
- `POST /items` - Créer un presqu'accident
- `PUT /items/{id}` - Mettre à jour
- `DELETE /items/{id}` - Supprimer (Admin/QHSE uniquement)

### Statistiques
- `GET /stats` - Stats globales (total, par service, par sévérité)
- `GET /rapport-stats` - Stats complètes pour rapport (+ délais, lieux, mois)
- `GET /badge-stats` - Stats pour badge notification (à traiter, en retard)
- `GET /alerts` - Alertes avec urgence (critique, important, normal)

### Upload & Import/Export
- `POST /items/{id}/upload` - Upload pièce jointe
- `POST /import` - Import CSV/Excel
- `GET /export/template` - Template CSV

---

## Modèle de données

```json
{
  "id": "uuid",
  "titre": "string (required)",
  "description": "string (required)",
  "date_incident": "ISO date (required)",
  "lieu": "string (required)",
  "service": "ADV|LOGISTIQUE|PRODUCTION|QHSE|MAINTENANCE|LABO|INDUS|AUTRE",
  "personnes_impliquees": "string (optional)",
  "declarant": "string (optional)",
  "contexte_cause": "string (optional)",
  "severite": "FAIBLE|MOYEN|ELEVE|CRITIQUE",
  "actions_proposees": "string (optional)",
  "actions_preventions": "string (optional)",
  "responsable_action": "string (optional)",
  "date_echeance_action": "ISO date (optional)",
  "status": "A_TRAITER|EN_COURS|TERMINE|ARCHIVE",
  "date_cloture": "ISO date (auto)",
  "commentaire": "string (optional)",
  "piece_jointe_url": "string (optional)",
  "piece_jointe_nom": "string (optional)",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp",
  "created_by": "user_id",
  "updated_by": "user_id"
}
```

---

## Permissions par rôle

- **ADMIN**: View, Edit, Delete
- **QHSE**: View, Edit, Delete (accès complet)
- **DIRECTEUR**: View, Edit
- **TECHNICIEN**: View, Edit, Delete
- **PROD/RSP_PROD/INDUS/LOGISTIQUE**: View, Edit
- **ADV/LABO**: View, Edit
- **VISUALISEUR**: View only

---

## Tests Backend

**Résultats:** 19/19 tests réussis ✅ (100%)

**Scénarios testés:**
1. ✅ Connexion admin
2. ✅ Création presqu'accidents (4 services différents)
3. ✅ Filtres multiples (service, statut, sévérité, lieu)
4. ✅ Détails item
5. ✅ Mises à jour et transitions de statut
6. ✅ Statistiques globales et calculs
7. ✅ Alertes et urgences
8. ✅ Badge stats
9. ✅ Rapport stats complet
10. ✅ Upload pièces jointes
11. ✅ Export template CSV
12. ✅ Import CSV
13. ✅ Suppression (admin)
14. ✅ Sécurité et authentification

---

## Installation & Déploiement

### 1. Migration des permissions

```bash
cd /app/backend
python migrations/add_presqu_accident_permissions.py
```

### 2. Redémarrage des services

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### 3. Vérification

- Backend: Vérifier les logs `/var/log/supervisor/backend.*.log`
- Frontend: Accéder à `/presqu-accident` dans l'interface

---

## Fonctionnalités clés

1. **Gestion complète du cycle de vie**
   - De la déclaration à la clôture
   - Suivi des actions correctives
   - Historique complet

2. **Système d'alertes intelligent**
   - Détection automatique des retards
   - Classification par urgence
   - Notifications badge

3. **Reporting avancé**
   - 3 modes de visualisation (Cards, Table, Charts)
   - KPIs multiples (services, sévérité, lieux)
   - Graphiques interactifs

4. **Import/Export**
   - Template CSV fourni
   - Import en masse
   - Export global ou filtré

5. **Audit & Sécurité**
   - Logging complet des actions
   - Permissions granulaires
   - Authentification JWT

---

## Compatibilité

- ✅ Identique au pattern "Plan de Surveillance"
- ✅ Intégré dans le système de permissions
- ✅ Compatible avec Import/Export global
- ✅ Audit logging inclus
- ✅ Responsive design

---

## Support

Pour toute question ou problème:
1. Vérifier les logs backend/frontend
2. Consulter la documentation API (Swagger: `/api/docs`)
3. Contacter l'équipe de développement
