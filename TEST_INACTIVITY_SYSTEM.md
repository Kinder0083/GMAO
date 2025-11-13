# Test du système de gestion d'inactivité et validation de token

## 🎯 Fonctionnalités implémentées

### 1. Token JWT à durée limitée (1 heure)
- Les tokens JWT générés lors du login sont maintenant valides **1 heure** (au lieu de 7 jours)
- Améliore la sécurité en limitant la durée de validité des sessions

### 2. Vérification silencieuse du token
- Au démarrage de l'application, le token est vérifié automatiquement
- Si le token est expiré ou invalide → déconnexion silencieuse et redirection vers login
- Si pas de token → redirection immédiate vers login
- **Résout le problème** : Un nouvel utilisateur n'arrive plus sur la session de l'ancien utilisateur

### 3. Déconnexion automatique après inactivité (15 minutes)
- Détection automatique de l'inactivité utilisateur
- Événements détectés : clics, mouvements souris, touches clavier, scroll, touch
- Après **15 minutes** d'inactivité → popup d'avertissement

### 4. Popup d'avertissement avec compte à rebours (60 secondes)
- Affiche un chronomètre dégressif de 60 secondes
- Deux options :
  - **"Rester connecté"** → Réinitialise le timer d'inactivité
  - **"Me déconnecter maintenant"** → Déconnexion immédiate
- Si aucune action après 60 secondes → déconnexion automatique

---

## 📋 Tests à effectuer

### TEST 1 : Vérification du token au démarrage (Résout le problème principal)

**Objectif** : Vérifier qu'un nouvel utilisateur n'accède plus à la session de l'ancien utilisateur

**Étapes** :
1. **Sur ordinateur A** :
   - Connectez-vous avec l'utilisateur A (ex: admin@gmao-iris.local)
   - Fermez simplement l'onglet/navigateur **SANS vous déconnecter**

2. **Sur le MÊME ordinateur A** (quelques minutes plus tard) :
   - Ouvrez le navigateur et accédez à l'URL de l'application
   - ✅ **Résultat attendu** : Vous arrivez sur la page de connexion (pas sur le dashboard de l'utilisateur A)
   - ✅ L'utilisateur B peut maintenant se connecter avec ses propres identifiants

3. **Vérification supplémentaire** :
   - Connectez-vous avec l'utilisateur B
   - Vérifiez que vous voyez bien le dashboard et les données de l'utilisateur B (pas de A)

**Note** : Ce test fonctionne car le token de l'utilisateur A a expiré (1 heure max) et est automatiquement détecté comme invalide.

---

### TEST 2 : Déconnexion après 15 minutes d'inactivité

**Objectif** : Tester le système de détection d'inactivité

**Étapes** :
1. Connectez-vous à l'application
2. Naviguez normalement pendant quelques secondes (pour initialiser le système)
3. **N'effectuez AUCUNE action** pendant 15 minutes (pas de clic, pas de mouvement de souris)
4. ✅ **Résultat attendu** : Après exactement 15 minutes, un popup orange apparaît avec le message "⚠️ Inactivité détectée"

**Raccourci de test (pour développement)** :
Si vous voulez tester plus rapidement, modifiez temporairement la durée dans `/app/frontend/src/components/Common/InactivityHandler.jsx` ligne 14 :
```javascript
const INACTIVITY_TIMEOUT = 1 * 60 * 1000; // 1 minute au lieu de 15
```

---

### TEST 3 : Popup d'avertissement avec compte à rebours

**Objectif** : Tester le popup et le chronomètre de 60 secondes

**Étapes** :
1. Suivez les étapes du TEST 2 jusqu'à l'apparition du popup
2. ✅ **Vérifications** :
   - Le popup affiche un grand chiffre (60, 59, 58, 57...)
   - Le compte à rebours diminue chaque seconde
   - Message : "Vous serez déconnecté automatiquement dans X secondes"
   - Deux boutons sont présents :
     - "Rester connecté" (bleu)
     - "Me déconnecter maintenant" (outline)

**TEST 3A : Bouton "Rester connecté"**
1. Cliquez sur **"Rester connecté"**
2. ✅ **Résultat attendu** :
   - Le popup se ferme immédiatement
   - Le timer d'inactivité est réinitialisé à 0
   - Vous restez connecté et pouvez continuer à travailler
   - Si vous restez à nouveau inactif 15 minutes → le popup réapparaît

**TEST 3B : Bouton "Me déconnecter maintenant"**
1. Attendez que le popup apparaisse
2. Cliquez sur **"Me déconnecter maintenant"**
3. ✅ **Résultat attendu** :
   - Déconnexion immédiate
   - Redirection vers la page de login
   - localStorage vidé (token et user supprimés)

**TEST 3C : Déconnexion automatique après 60 secondes**
1. Attendez que le popup apparaisse
2. **N'effectuez AUCUNE action** pendant les 60 secondes
3. ✅ **Résultat attendu** :
   - À 0 seconde, déconnexion automatique
   - Redirection vers la page de login
   - localStorage vidé

---

### TEST 4 : Token expiré (1 heure)

**Objectif** : Vérifier que le token expire bien après 1 heure

**Étapes** :
1. Connectez-vous à l'application
2. Laissez l'application ouverte dans un onglet (avec activité régulière pour éviter la déconnexion d'inactivité)
3. Attendez **1 heure et 5 minutes**
4. Essayez de naviguer vers une autre page ou de faire une action
5. ✅ **Résultat attendu** :
   - Déconnexion automatique
   - Redirection vers la page de login
   - Message possible : Token expiré

**Note** : Le système vérifie le token toutes les 30 secondes, donc la déconnexion peut avoir lieu légèrement après l'expiration.

---

### TEST 5 : Ordinateurs différents (vérification de non-régression)

**Objectif** : S'assurer que le système multi-utilisateurs fonctionne toujours

**Étapes** :
1. **Sur PC de bureau** : Connectez-vous avec l'utilisateur A
2. **Sur laptop** : Ouvrez l'application (même URL)
3. ✅ **Résultat attendu** :
   - Sur le laptop, vous arrivez sur la page de login (pas sur le dashboard de A)
   - Vous pouvez vous connecter avec l'utilisateur B
   - Les deux utilisateurs travaillent simultanément sans problème
   - Chaque utilisateur voit ses propres données

---

## 🐛 Problèmes résolus

### Problème initial
> "Lorsqu'un nouvel utilisateur veut accéder à la page de connexion, celui-ci arrive sur la session du dernier utilisateur"

### Causes identifiées
1. **localStorage persistant** : Le token restait dans le navigateur même après fermeture
2. **Pas de vérification d'expiration** : Le token de 7 jours restait valide très longtemps
3. **Pas de détection d'inactivité** : Sur ordinateur partagé, l'ancien utilisateur restait connecté

### Solutions implémentées
1. ✅ Token JWT réduit à **1 heure** au lieu de 7 jours
2. ✅ Vérification automatique du token au démarrage (silencieuse)
3. ✅ Déconnexion automatique après **15 minutes** d'inactivité
4. ✅ Popup d'avertissement **60 secondes** avant déconnexion
5. ✅ Nettoyage du localStorage lors de la déconnexion

---

## 📁 Fichiers modifiés

### Backend
- `/app/backend/server.py` (ligne 329-333) : Token JWT à 1 heure

### Frontend
- `/app/frontend/src/App.js` : Amélioration de `ProtectedRoute` avec validation token
- `/app/frontend/src/components/Common/InactivityHandler.jsx` : Nouveau composant de gestion d'inactivité
- `/app/frontend/src/components/Common/TokenValidator.jsx` : Nouveau composant de validation token
- `/app/frontend/src/components/Layout/MainLayout.jsx` : Intégration des nouveaux composants

---

## ⚙️ Configuration (si besoin d'ajuster)

### Modifier la durée d'inactivité
Fichier : `/app/frontend/src/components/Common/InactivityHandler.jsx`
```javascript
const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // Modifier ici (en millisecondes)
```

### Modifier la durée du compte à rebours
Fichier : `/app/frontend/src/components/Common/InactivityHandler.jsx`
```javascript
const WARNING_DURATION = 60 * 1000; // Modifier ici (en millisecondes)
```

### Modifier la durée de validité du token
Fichier : `/app/backend/server.py` (ligne 329)
```python
expires_delta=timedelta(hours=1)  # Modifier ici
```

---

## ✅ Checklist de validation complète

- [ ] TEST 1 : Nouvel utilisateur arrive bien sur page de login (pas sur session précédente)
- [ ] TEST 2 : Popup d'inactivité apparaît après 15 minutes
- [ ] TEST 3A : Bouton "Rester connecté" fonctionne
- [ ] TEST 3B : Bouton "Me déconnecter maintenant" fonctionne
- [ ] TEST 3C : Déconnexion automatique après 60 secondes fonctionne
- [ ] TEST 4 : Token expire bien après 1 heure
- [ ] TEST 5 : Plusieurs utilisateurs sur ordinateurs différents fonctionnent simultanément

---

**Tous les tests doivent être validés pour confirmer que le système fonctionne correctement ! 🎉**
