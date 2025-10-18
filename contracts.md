# Contrats API - GMAO Atlas

## Architecture
- **Frontend**: React avec données mockées dans `/frontend/src/mock/mockData.js`
- **Backend**: FastAPI avec MongoDB
- **Base de données**: MongoDB avec collections pour chaque entité

## Collections MongoDB

### 1. users (Utilisateurs)
```json
{
  "_id": ObjectId,
  "nom": String,
  "prenom": String,
  "email": String (unique),
  "password": String (hashed),
  "role": Enum["ADMIN", "TECHNICIEN", "VISUALISEUR"],
  "telephone": String,
  "statut": String,
  "dateCreation": DateTime,
  "derniereConnexion": DateTime
}
```

### 2. work_orders (Ordres de travail)
```json
{
  "_id": ObjectId,
  "numero": String (auto-generated, e.g., "5823"),
  "titre": String,
  "description": String,
  "statut": Enum["OUVERT", "EN_COURS", "EN_ATTENTE", "TERMINE"],
  "priorite": Enum["HAUTE", "MOYENNE", "BASSE", "AUCUNE"],
  "equipement_id": ObjectId (référence),
  "assigne_a_id": ObjectId (référence users),
  "emplacement_id": ObjectId (référence),
  "dateCreation": DateTime,
  "dateLimite": DateTime,
  "tempsEstime": Number (heures),
  "tempsReel": Number (heures),
  "dateTermine": DateTime
}
```

### 3. equipments (\u00c9quipements)
```json
{
  "_id": ObjectId,
  "nom": String,
  "categorie": String,
  "emplacement_id": ObjectId (référence),
  "statut": Enum["OPERATIONNEL", "EN_MAINTENANCE", "HORS_SERVICE"],
  "dateAchat": Date,
  "coutAchat": Number,
  "numeroSerie": String (unique),
  "garantie": String,
  "derniereMaintenance": Date,
  "specifications": Object,
  "dateCreation": DateTime
}
```

### 4. locations (Emplacements)
```json
{
  "_id": ObjectId,
  "nom": String,
  "adresse": String,
  "ville": String,
  "codePostal": String,
  "type": String,
  "coordinates": {
    "latitude": Number,
    "longitude": Number
  },
  "dateCreation": DateTime
}
```

### 5. inventory (Inventaire)
```json
{
  "_id": ObjectId,
  "nom": String,
  "reference": String (unique),
  "categorie": String,
  "quantite": Number,
  "quantiteMin": Number,
  "prixUnitaire": Number,
  "fournisseur": String,
  "emplacement": String,
  "dateCreation": DateTime,
  "derniereModification": DateTime
}
```

### 6. preventive_maintenance (Maintenance préventive)
```json
{
  "_id": ObjectId,
  "titre": String,
  "equipement_id": ObjectId (référence),
  "frequence": Enum["HEBDOMADAIRE", "MENSUEL", "TRIMESTRIEL", "ANNUEL"],
  "prochaineMaintenance": Date,
  "derniereMaintenance": Date,
  "assigne_a_id": ObjectId (référence users),
  "duree": Number (heures),
  "statut": Enum["ACTIF", "INACTIF"],
  "checklist": Array[String],
  "dateCreation": DateTime
}
```

### 7. vendors (Fournisseurs)
```json
{
  "_id": ObjectId,
  "nom": String,
  "contact": String,
  "email": String,
  "telephone": String,
  "adresse": String,
  "specialite": String,
  "dateCreation": DateTime
}
```

## Endpoints API

### Authentification
- `POST /api/auth/register` - Créer un compte
- `POST /api/auth/login` - Se connecter (retourne JWT token)
- `GET /api/auth/me` - Obtenir l'utilisateur connecté

### Ordres de travail
- `GET /api/work-orders` - Liste tous les ordres
- `GET /api/work-orders/{id}` - Détails d'un ordre
- `POST /api/work-orders` - Créer un ordre
- `PUT /api/work-orders/{id}` - Modifier un ordre
- `DELETE /api/work-orders/{id}` - Supprimer un ordre
- `GET /api/work-orders/stats` - Statistiques

### \u00c9quipements
- `GET /api/equipments` - Liste tous les équipements
- `GET /api/equipments/{id}` - Détails d'un équipement
- `POST /api/equipments` - Créer un équipement
- `PUT /api/equipments/{id}` - Modifier un équipement
- `DELETE /api/equipments/{id}` - Supprimer un équipement
- `GET /api/equipments/stats` - Statistiques

### Inventaire
- `GET /api/inventory` - Liste tous les articles
- `GET /api/inventory/{id}` - Détails d'un article
- `POST /api/inventory` - Créer un article
- `PUT /api/inventory/{id}` - Modifier un article
- `DELETE /api/inventory/{id}` - Supprimer un article
- `GET /api/inventory/low-stock` - Articles en stock bas

### Emplacements
- `GET /api/locations` - Liste tous les emplacements
- `GET /api/locations/{id}` - Détails d'un emplacement
- `POST /api/locations` - Créer un emplacement
- `PUT /api/locations/{id}` - Modifier un emplacement
- `DELETE /api/locations/{id}` - Supprimer un emplacement

### Maintenance préventive
- `GET /api/preventive-maintenance` - Liste toutes les maintenances
- `GET /api/preventive-maintenance/{id}` - Détails
- `POST /api/preventive-maintenance` - Créer
- `PUT /api/preventive-maintenance/{id}` - Modifier
- `DELETE /api/preventive-maintenance/{id}` - Supprimer

### Utilisateurs
- `GET /api/users` - Liste tous les utilisateurs
- `GET /api/users/{id}` - Détails d'un utilisateur
- `POST /api/users` - Créer un utilisateur
- `PUT /api/users/{id}` - Modifier un utilisateur
- `DELETE /api/users/{id}` - Supprimer un utilisateur

### Fournisseurs
- `GET /api/vendors` - Liste tous les fournisseurs
- `GET /api/vendors/{id}` - Détails d'un fournisseur
- `POST /api/vendors` - Créer un fournisseur
- `PUT /api/vendors/{id}` - Modifier un fournisseur
- `DELETE /api/vendors/{id}` - Supprimer un fournisseur

### Rapports
- `GET /api/reports/analytics` - Données analytiques générales
- `GET /api/reports/work-orders` - Rapport des ordres de travail
- `GET /api/reports/equipments` - Rapport des équipements
- `GET /api/reports/costs` - Rapport des coûts

## Intégration Frontend-Backend

### Étapes
1. Créer les modèles Pydantic pour chaque entité
2. Implémenter les routes CRUD pour chaque ressource
3. Ajouter l'authentification JWT
4. Remplacer les données mockées dans le frontend par des appels API
5. Gérer les états de chargement et erreurs

### Fichiers Frontend à modifier
- Supprimer `/frontend/src/mock/mockData.js`
- Créer `/frontend/src/services/api.js` pour centraliser les appels API
- Mettre à jour chaque page pour utiliser les vrais endpoints

### Sécurité
- Toutes les routes (sauf login/register) nécessitent un token JWT
- Les mots de passe sont hashés avec bcrypt
- Validation des données avec Pydantic
- CORS configuré pour le frontend uniquement
