# GMAO Iris - Notes de Version

## Version 1.16.0 - QR Code equipement : presqu'accident public, panne signalable sans compte, mode hors-ligne (Septembre 2026)

- **Correction (cause du bug rapporte)** : desactiver "Authentification requise" sur une action QR ("Signaler une panne", "Signaler un presqu'accident") n'avait aucun effet visible. Cause : ces deux actions redirigeaient vers une page protegee par connexion (`/work-orders`, `/presqu-accident`) quel que soit le reglage - seule "Creer une demande d'intervention" disposait d'un vrai parcours public (formulaire + route backend sans authentification). Le reglage ne pouvait donc jamais fonctionner pour ces deux actions, faute de mecanisme public correspondant.
- **Nouveau** : "Declarer un presqu'accident" est desormais un veritable parcours public - formulaire directement sur la page QR (titre, circonstances, gravite, photo en un tap), nouvelle route backend dediee sans authentification, notification automatique des administrateurs.
- **Nouveau** : "Signaler une panne" ouvre desormais le meme formulaire public rapide que "Creer une demande d'intervention" (au lieu de rediriger vers l'ecran de connexion).
- **Ergonomie** : la page QR separe visuellement les actions utilisables sans compte ("Sans compte") des actions reservees au personnel connecte, pour qu'un novice comprenne immediatement ce qu'il peut faire sans se connecter.
- **Nouveau (mode hors-ligne)** : si le reseau coupe au moment d'envoyer une demande ou une declaration depuis le QR, elle est enregistree localement sur l'appareil et transmise automatiquement des que la connexion revient - comme le reste de l'application.
- **Performance** : l'envoi des notifications email aux administrateurs (demande d'intervention et presqu'accident publics) se fait desormais en arriere-plan ; il pouvait auparavant bloquer la confirmation plusieurs secondes, voire dix secondes ou plus, si le serveur mail etait lent a repondre.
- **Renfort** : protection contre le double-tap sur les formulaires publics QR, qui pouvait creer des declarations/demandes en double (trouve pendant les tests de cette version).

## Version 1.15.3 - Correction : QR code equipement/formation inutilisable (Septembre 2026)

- **Correction (cause racine)** : la page publique ouverte en flashant le QR code d'un equipement (ou sous-equipement) affichait "Equipement introuvable" alors que l'equipement existait bien et que l'API repondait correctement. Cause : `QREquipmentPage.jsx` (et 5 autres fichiers : QR inventaire, formulaire d'intervention public, formulaire de surveillance, mode inventaire rapide, page de formation publique) lisaient directement la variable d'environnement de l'adresse backend SANS repli. Des que cette variable n'est pas definie au moment du build du frontend, elle vaut `undefined` en JavaScript, ce qui se retrouve litteralement dans l'URL des requetes (ex: `/qr/undefined/api/...`) - le serveur renvoyait alors la page d'accueil au lieu des donnees, faisant echouer le chargement.
- Ces pages utilisent desormais le meme utilitaire de repli fiable (`utils/config.js`, deja utilise par le reste de l'application) qui retombe automatiquement sur l'adresse du site actuel.
- Meme correctif applique a 2 actions du menu contextuel Documentations (Visualiser/Telecharger un document), a l'extraction IA et l'import en masse des presqu'accidents, et au renouvellement automatique silencieux du jeton de connexion.

## Version 1.15.2 - Correction : dossiers et enregistrements dupliques dans Documentations (Septembre 2026)

- **Correction (dossiers dupliques)** : un meme pole de service (ex: "Maintenance") pouvait apparaitre deux fois dans Documentations, avec les memes fichiers. Cause : contrairement a la plupart des collections de l'application, `poles_service` (et `doc_folders`, `documents`, `autorisations_particulieres`) n'etaient pas protegees par un index unique empechant deux enregistrements de partager le meme identifiant. Au passage, plusieurs enregistrements dupliques (jusqu'a 3 copies d'une meme autorisation particuliere) ont ete detectes et nettoyes automatiquement au demarrage - ce nettoyage est idempotent et s'appliquera aussi automatiquement lors de la mise a jour en production.
- **Correction (menu contextuel en double)** : dans la vue "Explorateur" de Documentations, un clic droit sur le fond (pour creer un nouveau dossier/document) pouvait faire apparaitre deux menus contextuels superposes lors d'un Ctrl+clic droit. Cause : le clic n'etait pas correctement stoppe et remontait jusqu'au menu contextuel global de l'application.
- **Renfort** : les formulaires de creation de pole/dossier sont desormais proteges contre un double-clic accidentel (qui pouvait creer deux enregistrements reels identiques).

## Version 1.15.1 - Correction : numero de version incoherent sur l'ecran de connexion (Septembre 2026)

- **Correction** : l'écran de connexion pouvait afficher un numéro de version différent de celui affiché dans le menu "Mise à jour". Cause : deux fichiers `version.json` distincts existaient dans le dépôt (`updates/version.json` à la racine, lu par le système de mise à jour, et `backend/updates/version.json`, lu par l'écran de connexion) - il suffisait qu'ils divergent pour produire l'incohérence. Le fichier en double a été supprimé ; l'écran de connexion lit désormais la même source unique que "Mise à jour".

## Version 1.15.0 - Affichage Dynamique : habillage visuel et nouveaux blocs (Septembre 2026)

### Visuel
- Alerte automatique (bordure pulsante + badge "ARRET"/"TRS BAS") sur le bloc Cadence equipement en cas d'arret ou de TRS sous objectif
- Icone et couleur d'accent propres a chaque type de bloc
- Modeles de mise en page prets a l'emploi ("Tableau de bord atelier", "Ecran d'accueil") a la creation d'un ecran
- En-tete personnalisable (logo, nom du site, horloge)
- Alignement automatique a la grille pendant le glisser-depose
- Theme clair disponible en plus du theme sombre (par ecran)
- Indicateur de mise a jour en direct (pastille + heure du dernier rafraichissement)

### Fonctionnel
- Mini-graphique (historique recent) sur les blocs Cadence, KPI et Capteur MQTT
- Nouveau bloc **Bandeau defilant** pour les annonces/consignes
- Nouveau bloc **QR Code** (genere cote serveur, scannable)
- Apercu plein ecran dans l'editeur, sans avoir a publier
- Rotation automatique entre plusieurs ecrans sur un meme afficheur physique (`?rotate=jeton2,jeton3&interval=20` sur le lien public)
- Annuler (Ctrl+Z) sur les deplacements/redimensionnements/ajouts/suppressions de blocs

## Version 1.14.2 - Correction : liste des equipements vide dans le bloc Cadence (Septembre 2026)

- **Correction** : dans l'editeur Affichage Dynamique, le bloc "Cadence equipement" affichait une liste "Equipement" vide. Cause : les machines M.E.S. n'ont pas de nom en propre (leur nom vient de l'equipement auquel elles sont rattachees) - la route qui alimentait cette liste ne recuperait jamais ce nom et renvoyait systematiquement une chaine vide. Corrige pour aller chercher le vrai nom d'equipement, comme le fait deja le module M.E.S. lui-meme.

## Version 1.14.1 - Correction : menu Affichage Dynamique invisible (Septembre 2026)

- **Correction** : le menu "Affichage Dynamique" n'apparaissait pas dans la barre laterale malgre la mise a jour 1.14.0. Cause : trois listes de menu dupliquees existent dans le code (sidebar, ecran de personnalisation du menu, selecteur de page de demarrage) - seule l'une d'elles avait ete mise a jour lors de l'ajout initial de la fonctionnalite. Les trois sont desormais synchronisees.

## Version 1.14.0 - Affichage Dynamique, Mise a jour fiabilisee, Moteur TRS unifie (Septembre 2026)

### M.E.S.
- **Zoom par selection glissee** sur le graphique Historique des cadences
- **Moteur de calcul TRS unifie** (`backend/mes_schedule.py`) : le tableau de bord temps reel, l'historique/tendance, les rapports PDF/Excel et la page Rapports (vue d'ensemble/heatmap) utilisaient jusqu'ici 4 formules independantes pouvant afficher un TRS different pour la meme machine/periode - desormais un seul point de calcul partage
- **Rythmes de cadence par creneau horaire** : une machine peut avoir plusieurs cadences theoriques selon le creneau (ex: 90 cp/min en journee, 45 cp/min la nuit) au lieu d'une seule cadence fixe
- **Correction des postes de nuit** a cheval sur minuit (ex: 22h-6h) : ne forcent plus la disponibilite/le TRS a 0 et ne desactivent plus les alertes toute la nuit
- **Pauses planifiees preservees** lors du changement de reference produit (elles etaient auparavant silencieusement effacees)
- **Machines ESP32** (compteur cumule) : les rapports et le graphique de tendance affichaient une production quasi nulle (lecture d'une table vide pour ce mode) - corrige
- **Calculs alignes sur le fuseau horaire configure** (DST-aware) au lieu de l'UTC brut

### Affichage Dynamique (nouveau module)
- Nouvelle page de signaletique 100% personnalisable par blocs glisser-deposer : cadence equipement, capteur MQTT, texte libre, image/logo, horloge, statut equipements, ordres du jour, KPI/graphique
- Geree en permissions comme les autres modules de l'application
- Lien public par ecran (jeton unique non devinable), consultable sans authentification, strictement en lecture seule - concu pour les lecteurs de signaletique type Yodeck/OptiSigns

### Mise a jour (menu in-app)
- Le bouton "Mettre a jour maintenant" fonctionne desormais de bout en bout : redemarrage cible du service applicatif au lieu d'un reboot complet du serveur, suivi en direct du journal de mise a jour, detection de version fiabilisee (n'utilise plus l'API GitHub limitee a 60 requetes/heure)
- Le rollback vers une version anterieure reinstalle desormais reellement les dependances et redemarre le service, au lieu de se contenter de changer le code sur disque

## Version 1.13.0 - Independance vis-a-vis d'Emergent pour l'IA (Avril 2026)

### IA
- **Suppression de la dependance a `emergentintegrations`** (SDK proprietaire de la plateforme Emergent, installable uniquement via un index prive) sur les 18 fichiers backend qui l'utilisaient
- Nouveau module `backend/llm_service.py` : couche d'acces unifiee aux LLM via `litellm`, appelant directement les fournisseurs (OpenAI, Anthropic/Claude, Google Gemini, DeepSeek, Mistral) avec les cles API propres de chaque installation
- **DeepSeek et Mistral fonctionnent desormais reellement** dans l'assistant Adria : le selecteur de modele basculait silencieusement sur Gemini quand ces fournisseurs etaient choisis, sans jamais les appeler
- Parametres > Cles API LLM : ajout des champs OpenAI, Anthropic et Google Gemini (auparavant seuls DeepSeek et Mistral etaient proposes, les 3 autres passaient par la cle Emergent)
- Plus de cle `EMERGENT_LLM_KEY` codee en dur dans le script d'installation ; `.env.example` documente desormais les 5 variables de cles fournisseur

## Version 1.12.1 - Securite : compte de secours a l'installation (Avril 2026)

### Securite
- **Suppression du compte administrateur de secours code en dur** (`buenogy@gmail.com` / `Admin2024!`) qui etait cree automatiquement et identiquement sur chaque installation
- Le script `gmao-iris-install.sh` demande desormais l'email et le mot de passe du compte de secours a l'installateur (optionnel, laisser vide pour ne pas en creer) ; ce compte est propre a chaque installation

## Version 1.12.0 - M.E.S. ESP32, Coherence des Donnees & Pointages (Avril 2026)

### M.E.S. — Migration vers une architecture ESP32 edge-computing
- **Decentralisation du calcul de cadence** : chaque machine (ESP32) calcule localement et publie sur MQTT. Le backend ne stocke plus de pulses bruts, supprimant les bloats MongoDB qui causaient des erreurs `QueryExceededMemoryLimitNoDiskUseAllowed`
- **Deux modes de comptage** au choix dans la config M.E.S. : `Imp` (impulsions traditionnelles) et `cp/min` (cadence directe envoyee par l'ESP32)
- **Etats explicites** : ecoute du topic `mqtt_topic_state` (ACTIVE / IDLE) au lieu de deduire l'etat par detection de pulses
- **Hierarchie Parent / Sous-equipement** : le dropdown equipement est decompose en deux selecteurs pour les lignes de production complexes
- **Total cumule** : suivi du compteur total publie par l'ESP32 via `mqtt_topic_total`
- **Agregations multi-niveaux** automatiques :
  - `mes_cadence_history` (1 doc/machine/minute)
  - `mes_daily_summary` (1 doc/machine/jour)
  - `mes_shift_summary` (1 doc/machine/poste 3x8)
- **Rapports 3x8 shifts** declenches par le topic MQTT `mqtt_topic_shift_end`
- **Indexes MongoDB optimises** (script `ensure_mes_indexes.py`)
- **Delai de retention configurable** depuis l'UI (Parametres -> Donnees)

### M.E.S. — Refonte complete de la page Rapports
- **Onglet Vue d'ensemble** : KPIs site (TRS global, production totale, machines actives), Top/Flop des machines par TRS, heatmap horaire, metriques par poste
- **Onglet Detail par machine** : cadence par minute, distribution horaire, comparaison entre periodes
- **Filtres avances** : periode (jour, semaine, mois, custom), machines, postes
- Endpoint `GET /api/mes/reports/overview`

### Gestion automatique du fuseau horaire (DST)
- **Plus besoin d'ajuster manuellement** l'offset 2 fois par an au passage heure d'ete / hiver
- Module `timezone_helper.py` base sur Python `zoneinfo`
- Configurable depuis Parametres -> Fuseau horaire

### Panneau "Coherence des donnees" (Parametres speciaux)
- **Scan + reparation** des incoherences connues en base avec mode dry-run (Simuler) avant Reparer
- 4 checks disponibles :
  - `user_actif_statut_sync` : champ legacy `actif` desync de `statut`
  - `service_responsables_duplicates` : doublons (service, user_id)
  - `time_entries_integrity` : timestamps en string, user_id non-canoniques, orphelins
  - `orphan_user_assignments` (informational) : pointages assignes a un utilisateur supprime, avec **modal "Reassigner"** integre pour transferer en masse vers un utilisateur actif
  - `work_orders_duplicate_numero` : plusieurs ordres de travail portant le meme numero (#XXXX). Reparation automatique : l'OT le plus ancien garde son numero, les autres sont renumerotes avec de nouveaux numeros uniques ; le compteur atomique est resynchronise pour eviter toute collision future
- Endpoints REST : `GET /api/admin/data-integrity/scan`, `POST /api/admin/data-integrity/repair`, `GET /api/admin/data-integrity/last-scan`
- **Architecture extensible** : ajouter un check = 1 entree dans le dict `CHECKS` de `routes/data_integrity.py`

### Surveillance proactive de la coherence
- **Scan quotidien automatique** a 02h30 via APScheduler. Si des incoherences sont detectees, un email d'alerte est envoye aux destinataires configures (cooldown 24h)
- **Badge topbar "Coherence des donnees"** (admin uniquement) : icone Database avec compteur orange si issues, point vert si OK, refresh auto 5min
- **Card dediee dans Sante systeme** : statut du dernier scan + bouton "Scanner maintenant"
- **Nouveau type d'alerte email `data_integrity`** configurable dans la section Alertes Email

### Corrections de bugs
- **Widget "Charge OT restante" du Dashboard** : ne comptait qu'un seul technicien sur certaines bases. Cause : filtre cumulatif sur `actif` (legacy stale) ET `statut`. Fix : filtre sur `statut` uniquement (source de verite UI)
- **Rapport "Pointage horaire du personnel"** : les modifications de date sur les time_entries d'OT/amelioration ne remontaient plus dans le rapport apres edit. Cause racine : timestamp stocke en string au lieu de datetime, invisible au filtre `$gte/$lte` MongoDB. Fix appliquee + check `time_entries_integrity` pour reparer les vieilles entries
- **Erreur 500 `QueryExceededMemoryLimitNoDiskUseAllowed`** sur le M.E.S : eliminee par la migration vers les agregations ESP32
- **Page Rapports M.E.S. blanche** : declaration d'etat manquante corrigee dans `MESReportsPage.jsx`

### Scripts de migration et diagnostic
- `scripts/diagnose_charge_ot_widget.py` : diagnostic complet du widget Charge OT
- `scripts/cleanup_user_actif_field.py` : resync `actif` <- `statut` (avec dry-run)
- `scripts/dedupe_service_responsables.py` : dedoublonnage (avec dry-run)
- `scripts/migrate_to_esp32_archi.py` : migration de l'architecture M.E.S.
- `scripts/ensure_mes_indexes.py` : creation des indexes MongoDB du module M.E.S.
- `scripts/normalize_user_ids.py` : normalisation UUID -> ObjectId

---

## Version 1.10.0 - Demandes d'Intervention, Drag & Drop, IA Achats (Mars 2026)

### Glisser-Deposer (Drag & Drop) pour les Pieces Jointes
- **Zone de depot visuelle** ajoutee aux 3 formulaires de l'application : Ordres de Travail, Demandes d'Intervention et formulaire public DI via QR Code
- Les utilisateurs peuvent desormais glisser-deposer des fichiers depuis leur bureau directement dans les formulaires
- Feedback visuel : bordure en pointilles qui devient bleue au survol, avec icone et message "Deposez vos fichiers ici"
- Les boutons existants "Parcourir" et "Appareil photo" sont conserves a l'interieur de la zone de depot
- Validation automatique de la taille des fichiers (max 25 Mo)

### Miniatures des Pieces Jointes dans les Ordres de Travail
- Les photos et images sont desormais affichees en miniatures dans le formulaire de **modification** des Ordres de Travail (icone crayon), en plus du dialogue de visualisation (icone oeil)
- Les images protegees sont chargees via des blob URLs authentifies avec nettoyage automatique de la memoire a la fermeture du formulaire
- Protection contre les mises a jour d'etat asynchrones perimees (race condition)

### Creation de Demandes d'Intervention Publiques via QR Code
- **Formulaire mobile epure** : les utilisateurs non authentifies (operateurs, sous-traitants, visiteurs) peuvent creer une Demande d'Intervention directement depuis la page QR d'un equipement
- Photos joignables par glisser-deposer, appareil photo ou galerie
- Le formulaire requiert uniquement : nom du demandeur, titre et description

### Notifications Email pour DI Publiques
- **Email automatique** envoye aux responsables maintenance lors de la creation d'une DI publique
- L'email contient les details de la demande et deux boutons d'action integres :
  - **"Convertir en OT"** : ouvre l'application sur la page des DI et declenche la conversion en Ordre de Travail
  - **"Refuser"** : ouvre l'application et declenche le refus de la demande

### KPI Demandes d'Intervention sur le Dashboard
- **Deux nouveaux indicateurs** sur le tableau de bord principal :
  - Nombre de DI en attente de traitement
  - Temps de reponse moyen des DI
- Mise a jour en temps reel via l'endpoint `/api/stats/intervention-requests`

### IA - Analyse de l'Historique des Achats
- **Analyse IA des achats** : Bouton "Analyse IA" sur la page Historique Achat pour analyser automatiquement les tendances de depenses, fournisseurs recurrents et optimisations
- **Archives IA** : Consultation de l'historique de toutes les analyses IA effectuees sur les achats

### Cache-Busting Automatique
- Plus besoin de `CTRL+MAJ+F5` apres une mise a jour : le navigateur detecte automatiquement les nouvelles versions
- Un fichier `version.json` est mis a jour a chaque build
- Le hook React `useVersionCheck` verifie toutes les 5 minutes + au retour sur l'onglet et recharge la page automatiquement

### Corrections de Bugs
- **Permissions admin** : les administrateurs peuvent desormais modifier leurs propres permissions
- **Suppression DI** : la suppression des Demandes d'Intervention est de nouveau possible pour les utilisateurs autorises
- **Logique des icones DI** : le crayon (modifier) disparait apres conversion en OT, remplace par l'oeil (visualiser)
- **Photos DI avant conversion** : les miniatures sont visibles dans le formulaire de modification AVANT la conversion en OT
- **Transfert photos DI vers OT** : la copie des pieces jointes lors de la conversion DI vers OT est fiabilisee avec support des anciens et nouveaux formats

---

## Version 1.6.0 - MISE A JOUR MAJEURE IA & QHSE (Fevrier 2026)

### Intelligence Artificielle - Checklists & Maintenance

#### Generation IA de Checklists
- Upload d'un document technique (PDF, image, texte), l'IA genere automatiquement un template de checklist complet
- Les items generes incluent les points de controle, criteres d'acceptation et niveaux de criticite
- Acces depuis le module "Gestion des Checklists" via le bouton "Generer avec IA"

#### Generation IA de Programmes de Maintenance
- Upload d'une documentation constructeur, l'IA genere un plan de maintenance preventive detaille
- Inclut periodicite, taches, competences requises et pieces necessaires
- Acces depuis le module "Maintenance Preventive"

#### Analyse IA des Non-Conformites
- Analyse automatique de l'historique des executions de checklists
- Detection des patterns recurrents de non-conformites, tendances negatives, equipements a risque
- Suggestions d'actions correctives avec ordres de travail curatifs creables en 1 clic
- Envoi automatique d'alertes email aux responsables de service concerne en cas de patterns critiques

### Intelligence Artificielle - Presqu'accidents

#### Analyse IA des Causes Racines
- Methode 5 Pourquoi automatisee : l'IA genere les 5 niveaux de questionnement et identifie la cause racine
- Diagramme Ishikawa (6M) : analyse structuree par Milieu, Materiel, Methode, Main d'oeuvre, Matiere, Management
- Proposition d'actions preventives classees par priorite (HAUTE/MOYENNE/BASSE) avec delais recommandes
- Evaluation automatique severite/recurrence applicable en 1 clic au formulaire de traitement
- Prise en compte de l'historique des incidents pour identifier les recurrences
- Acces via le bouton "Analyser avec IA" dans le dialogue de traitement

#### Detection Automatique d'Incidents Similaires
- Lors de la saisie d'un nouveau presqu'accident, l'IA recherche automatiquement les incidents similaires
- Declenchement automatique apres 2 secondes de saisie (minimum 15 caracteres de description)
- Affichage du score de similarite, de la raison de la similarite et des lecons a retenir
- Recommandations basees sur les actions deja entreprises pour les incidents precedents

#### Analyse IA des Tendances Globales
- Analyse de l'ensemble des presqu'accidents pour identifier les tendances
- Detection des patterns recurrents classes par severite (CRITIQUE/IMPORTANT/MODERE)
- Identification des zones a risque avec niveau de risque et nombre d'incidents
- Predictions de risques futurs avec probabilite et actions preventives suggerees
- Analyse des facteurs contributifs (humain, materiel, organisationnel, environnemental)
- Recommandations prioritaires avec impact attendu et service concerne
- Envoi automatique d'alertes email aux responsables de service concerne
- Acces depuis le module "Rapport Presqu'accidents" via le bouton "Analyse IA"

#### Rapport de Synthese QHSE
- Generation automatique d'un rapport de synthese structure pour reunion QHSE
- Resume executif, indicateurs cles (total, taux traitement, en retard, tendance)
- Analyse par service et par categorie d'incident
- Top risques classes par gravite
- Plan d'action propose avec priorites, responsables, echeances et resultats attendus
- Conclusion et points de vigilance
- Option d'impression directe du rapport
- Acces depuis le module "Rapport Presqu'accidents" via le bouton "Rapport QHSE"

### Formulaire Presqu'accidents Enrichi

#### 7 Nouvelles Rubriques
- **Categorie d'incident** : Chute personne, Chute objet, Brulure, Coincement, Coupure, Collision, Exposition chimique, Electrique, Ergonomique, Projection, Incendie/Explosion, Autre
- **Equipement lie** : Association directe avec un equipement de la base GMAO
- **Mesures immediates prises** : Actions realisees sur le moment pour securiser la zone
- **Type de lesion potentielle** : Fracture, Brulure, Coupure, Contusion, Entorse, Intoxication, etc.
- **Temoins** : Personnes ayant assiste a l'incident (distinct des personnes impliquees)
- **Conditions au moment de l'incident** : Poste, meteo, fatigue, charge de travail, etc.
- **Facteurs contributifs** : Selection multiple parmi Humain, Materiel, Organisationnel, Environnemental

#### Reorganisation du Formulaire
- 7 sections claires avec fieldset : Identification, Description, Personnes, Evaluation, Equipement, Actions, Pieces jointes
- Placeholders explicatifs dans chaque champ pour guider la saisie
- Boutons toggle pour les facteurs contributifs (selection/deselection intuitive)
- Descriptions contextuelles pour les niveaux de gravite

### Alertes Email Automatiques
- Systeme d'alerte automatique connecte aux analyses IA
- Envoi d'email HTML formate au responsable du service concerne
- Notification in-app simultanee dans le systeme d'alertes
- Template email professionnel avec statistiques, patterns critiques et lien vers l'application
- Fallback : notification a tous les responsables si le service ne peut etre determine

### Corrections et Ameliorations
- Correction critique du systeme RBAC (permissions par module) pour les utilisateurs non-admin
- Migration automatique des permissions au demarrage pour corriger les donnees existantes
- Plan de surveillance : onglets par annee avec generation automatique des controles recurrents

### Visite Guidee Personnalisee par Profil
- La visite guidee est desormais adaptee au service de l'utilisateur connecte
- 6 profils disponibles : Maintenance, Production, QHSE, Logistique/ADV, Direction, Generique (fallback)
- Etapes communes conservees pour tous (menu, dashboard, notifications, chat, assistant IA)
- Etapes specifiques au metier avec textes adaptes (ex: "Consultez les OT qui vous sont assignes" pour Maintenance, "Suivez les indicateurs securite" pour Direction)
- Admin sans service defini recoit la visite Direction
- Utilisateur sans service defini recoit la visite Generique
- La visite peut etre relancee depuis les parametres

---

## Version 1.2.0 - MISE A JOUR MAJEURE (Octobre 2024)

### ✨ Nouvelles Fonctionnalités

#### Statistiques Historique Achat
- **Statistiques par utilisateur (créateur de commandes)**
  - Affichage du nombre de commandes passées par utilisateur (sans doublons)
  - Montant total dépensé par membre
  - Pourcentage du budget total avec barres de progression
  - Basé sur la colonne L (Creation User) du fichier Requêteur

- **Évolution mensuelle des achats**
  - Statistiques détaillées par mois
  - Nombre de commandes et montant par période
  - Graphiques avec barres de progression
  - Affichage des 12 derniers mois

#### Système de Notifications
- **Rafraîchissement automatique des notifications**
  - Mise à jour toutes les 30 secondes sans F5
  - Compteur dynamique d'ordres de travail assignés
  - Badge rouge avec nombre sur la cloche de notification

### 🔧 Corrections Critiques

#### Authentification Externe
- **FIX : Connexion externe maintenant fonctionnelle**
  - Correction variable JWT (SECRET_KEY vs JWT_SECRET_KEY) dans auth.py
  - Ajout SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES dans .env
  - Résolution du problème "Utilisateur ou mot de passe incorrect" en externe
  - Fonctionne maintenant sur tous les réseaux (local et externe)

#### Envoi d'Emails
- **FIX : Configuration SMTP Gmail fonctionnelle**
  - Support SMTP externe avec authentification (Gmail, SendGrid, etc.)
  - Configuration automatique via .env
  - Logs détaillés pour diagnostic
  - Chargement dynamique des variables d'environnement
  - Invitations membres opérationnelles

#### Système de Mise à Jour
- **Amélioration de la détection de versions**
  - Détection du commit local via git
  - Comparaison avec le commit distant GitHub
  - Affichage "Mise à jour disponible" seulement si différent

### 🐛 Corrections de Bugs

- Fix compteurs équipements (affichait 1 au lieu de 0)
- Fix masquage compte de secours (buenogy@gmail.com) sauf pour admin
- Fix colonne "Année de Fabrication" dans équipements (remplace "Garantie")
- Fix rafraîchissement notifications (plus besoin de F5)
- Fix détection ordres de travail assignés

---

## Version 1.1.0 (Octobre 2024)

### Fonctionnalités
- Section "Historique Achat" complète
- Import/Export CSV/Excel
- Affichage groupé par commande
- Système de mise à jour intégré
- Logo personnalisé
- Droits utilisateurs avec propriété

---

### 🔴 CORRECTION CRITIQUE - BUG LOGIN PROXMOX

**Problème Identifié:**
Le script Proxmox (`gmao-iris-proxmox.sh`) contenait une **erreur critique** qui empêchait la connexion sur les installations Proxmox :
- Ligne 344: `db = client.gmao_iris` (nom de base de données EN DUR)
- L'application utilisait `db = client[os.environ.get('DB_NAME')]`
- **Résultat:** Les utilisateurs étaient créés dans une base mais l'application les cherchait dans une autre

### ✅ Solutions Appliquées

#### 1. **Script Proxmox Corrigé** (`gmao-iris-proxmox.sh`)
- ✅ Remplacement de `db = client.gmao_iris` par `db = client[db_name]`
- ✅ Ajout du chargement des variables d'environnement
- ✅ Export explicite de `MONGO_URL` et `DB_NAME` lors de l'exécution
- ✅ Utilisation cohérente de la configuration

#### 2. **Scripts de Réparation Créés**
- ✅ `fix-proxmox-login.sh` : Diagnostic complet et correction
- ✅ `quick-create-admin.sh` : Création rapide d'admin

#### 3. **Utilisation des Scripts de Réparation**

**Sur votre serveur Proxmox, depuis le HOST:**
```bash
# Entrer dans le container
pct enter <CTID>

# Télécharger et exécuter le script de correction
wget https://raw.githubusercontent.com/votreuser/gmao-iris/main/fix-proxmox-login.sh
chmod +x fix-proxmox-login.sh
./fix-proxmox-login.sh
```

**OU version rapide:**
```bash
pct enter <CTID>
wget https://raw.githubusercontent.com/votreuser/gmao-iris/main/quick-create-admin.sh
chmod +x quick-create-admin.sh
./quick-create-admin.sh
```

### 🔍 Diagnostic
Le script de correction effectue:
1. Vérification de la configuration (.env)
2. Vérification de MongoDB et des bases de données
3. Comptage des utilisateurs existants
4. Création/réinitialisation du compte admin
5. Redémarrage du backend

---

## Version 1.0.0 - Corrections Critiques Login & Proxmox (Octobre 2025)

### 🔧 Corrections Critiques

#### 1. **Correction de la Création d'Utilisateurs**
- **Problème:** Les utilisateurs créés via le script Proxmox n'avaient pas tous les champs requis
- **Solution:** 
  - Ajout du champ `id` (UUID) obligatoire
  - Ajout du champ `statut` avec valeur "actif" (remplace `actif: True`)
  - Ajout du champ `service` (nullable)
  - Correction de `derniereConnexion` pour utiliser datetime au lieu de None
  
#### 2. **Configuration MongoDB**
- **Problème:** MONGO_URL contenait le nom de la base de données
- **Solution:**
  - Séparation de `MONGO_URL` et `DB_NAME` dans `.env`
  - `MONGO_URL=mongodb://localhost:27017`
  - `DB_NAME=gmao_iris`

#### 3. **Script Proxmox (`gmao-iris-proxmox.sh`)**
- Correction de la création d'utilisateurs avec tous les champs requis
- Ajout de la gestion des IDs avec UUID
- Correction du format des permissions
- Meilleure gestion des utilisateurs existants (mise à jour vs création)
- Création automatique d'un compte de secours:
  - Email: `buenogy@gmail.com`
  - Mot de passe: `Admin2024!`

#### 4. **Fichiers Backend**
- `server.py`: Ajout de logs de débogage pour le login (temporaires)
- `models.py`: Vérification des modèles Pydantic
- `.env.example`: Création d'un template pour la configuration

#### 5. **Fichiers Frontend**
- `.env.example`: Création d'un template pour la configuration
- `Login.jsx`: Interface mise à jour avec branding "GMAO Iris"

### 📝 Nouveaux Scripts

#### `create_admin.py` (Racine du projet)
Script interactif pour créer des administrateurs manuellement:
```bash
python3 create_admin.py
```

Fonctionnalités:
- Création interactive d'administrateurs
- Validation des emails et mots de passe
- Gestion des utilisateurs existants (mise à jour)
- Compatible avec la structure MongoDB complète

### 📚 Documentation

#### `INSTALLATION_PROXMOX_COMPLET.md`
Guide complet d'installation incluant:
- Installation automatique via script
- Installation manuelle étape par étape
- Configuration SSL avec Let's Encrypt
- Gestion et maintenance du container
- Dépannage et résolution de problèmes
- Procédures de sauvegarde

### ✅ Tests Validés

1. **Création d'utilisateurs:** ✅
   - Via script Proxmox
   - Via `create_admin.py`
   - Via l'interface web

2. **Login:** ✅
   - Authentification backend
   - Authentification frontend
   - Stockage du token
   - Navigation après login

3. **MongoDB:** ✅
   - Connexion correcte
   - Base de données `gmao_iris`
   - Structure des documents utilisateurs

### 🔐 Sécurité

**Important:** Après l'installation Proxmox:
1. Changez le mot de passe du compte de secours `buenogy@gmail.com`
2. Ou supprimez ce compte si non nécessaire
3. Générez une nouvelle `SECRET_KEY` en production:
   ```bash
   openssl rand -hex 32
   ```

### 🚀 Déploiement

#### Proxmox
```bash
wget -qO - https://raw.githubusercontent.com/votreuser/gmao-iris/main/gmao-iris-proxmox.sh | bash
```

#### Docker (À venir)
Documentation Docker à compléter dans une prochaine version.

### 📋 Structure de la Base de Données

#### Collection `users`
```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-string",           // UUID v4
  "email": "user@example.com",
  "password": "bcrypt-hash",
  "prenom": "John",
  "nom": "Doe",
  "role": "ADMIN|TECHNICIEN|VISUALISEUR",
  "telephone": "+33612345678",
  "service": "IT",               // Nullable
  "statut": "actif|inactif",
  "dateCreation": ISODate("..."),
  "derniereConnexion": ISODate("..."),
  "permissions": {
    "dashboard": {"view": true, "edit": true, "delete": true},
    "workOrders": {"view": true, "edit": true, "delete": true},
    "assets": {"view": true, "edit": true, "delete": true},
    "preventiveMaintenance": {"view": true, "edit": true, "delete": true},
    "inventory": {"view": true, "edit": true, "delete": true},
    "locations": {"view": true, "edit": true, "delete": true},
    "vendors": {"view": true, "edit": true, "delete": true},
    "reports": {"view": true, "edit": true, "delete": true}
  }
}
```

### 🐛 Bugs Connus

Aucun bug critique connu à ce jour.

### 📞 Support

Pour toute question:
1. Consultez `INSTALLATION_PROXMOX_COMPLET.md`
2. Vérifiez les logs: `/var/log/gmao-iris-backend.*.log`
3. Ouvrez une issue sur GitHub

---

## Versions Précédentes

### Version 0.9
- Interface utilisateur complète
- Gestion des ordres de travail
- Gestion des équipements
- Maintenance préventive
- Gestion d'inventaire
- Rapports et analytics

---

**Développé par:** Grèg  
**License:** Propriétaire  
**Contact:** support@gmao-iris.local
