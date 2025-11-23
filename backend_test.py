#!/usr/bin/env python3
"""
Backend API Testing Script for GMAO Application
Tests GET /api/inventory/stats endpoint
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Use the correct backend URL from frontend .env
BACKEND_URL = "https://maintenance-pro-23.preview.emergentagent.com/api"

# Test credentials - admin account as specified in the request
ADMIN_EMAIL = "admin@gmao-iris.local"
ADMIN_PASSWORD = "Admin123!"

class InventoryStatsTester:
    def __init__(self):
        self.admin_session = requests.Session()
        self.admin_token = None
        self.admin_data = None
        self.inventory_data = None
        self.stats_data = None
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_admin_login(self):
        """Test admin login with specified credentials"""
        self.log("Testing admin login...")
        
        try:
            response = self.admin_session.post(
                f"{BACKEND_URL}/auth/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.admin_data = data.get("user")
                
                # Set authorization header for future requests
                self.admin_session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log(f"✅ Admin login successful - User: {self.admin_data.get('prenom')} {self.admin_data.get('nom')} (Role: {self.admin_data.get('role')})")
                return True
            else:
                self.log(f"❌ Admin login failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Admin login request failed - Error: {str(e)}", "ERROR")
            return False
    
    def test_get_inventory_data(self):
        """TEST 1: Récupérer les données d'inventaire pour validation"""
        self.log("🧪 TEST 1: Récupération des données d'inventaire")
        
        try:
            # GET /api/inventory - Récupérer tous les items d'inventaire
            self.log("📦 Récupération de l'inventaire complet...")
            response = self.admin_session.get(f"{BACKEND_URL}/inventory", timeout=15)
            
            if response.status_code == 200:
                self.inventory_data = response.json()
                self.log(f"✅ Inventaire récupéré - {len(self.inventory_data)} articles trouvés")
                
                # Analyser les données pour comprendre la répartition
                rupture_count = 0
                niveau_bas_count = 0
                normal_count = 0
                
                for item in self.inventory_data:
                    quantite = item.get('quantite', 0)
                    quantite_min = item.get('quantiteMin', 0)
                    nom = item.get('nom', 'N/A')
                    
                    if quantite <= 0:
                        rupture_count += 1
                        self.log(f"   📉 RUPTURE: {nom} (Quantité: {quantite})")
                    elif quantite <= quantite_min:
                        niveau_bas_count += 1
                        self.log(f"   ⚠️ NIVEAU BAS: {nom} (Quantité: {quantite}, Min: {quantite_min})")
                    else:
                        normal_count += 1
                
                self.log(f"📊 Analyse inventaire:")
                self.log(f"   - Articles en rupture (quantité <= 0): {rupture_count}")
                self.log(f"   - Articles niveau bas (0 < quantité <= quantiteMin): {niveau_bas_count}")
                self.log(f"   - Articles normaux: {normal_count}")
                self.log(f"   - Total alertes attendues: {rupture_count + niveau_bas_count}")
                
                return True
            else:
                self.log(f"❌ Récupération inventaire échouée - Status: {response.status_code}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed - Error: {str(e)}", "ERROR")
            return False
    
    def test_inventory_stats_endpoint(self):
        """TEST 2: Tester l'endpoint GET /api/inventory/stats"""
        self.log("🧪 TEST 2: Test de l'endpoint GET /api/inventory/stats")
        
        try:
            # GET /api/inventory/stats
            self.log("📊 Appel de l'endpoint /api/inventory/stats...")
            response = self.admin_session.get(f"{BACKEND_URL}/inventory/stats", timeout=15)
            
            if response.status_code == 200:
                self.stats_data = response.json()
                self.log("✅ Endpoint /api/inventory/stats répond correctement (200 OK)")
                
                # Vérifier la structure de la réponse
                if 'rupture' in self.stats_data and 'niveau_bas' in self.stats_data:
                    rupture = self.stats_data.get('rupture')
                    niveau_bas = self.stats_data.get('niveau_bas')
                    
                    self.log(f"✅ Réponse contient les champs requis:")
                    self.log(f"   - rupture: {rupture}")
                    self.log(f"   - niveau_bas: {niveau_bas}")
                    
                    # Vérifier que les valeurs sont des entiers >= 0
                    if isinstance(rupture, int) and rupture >= 0:
                        self.log(f"✅ Champ 'rupture' est un entier >= 0: {rupture}")
                    else:
                        self.log(f"❌ Champ 'rupture' invalide: {rupture} (type: {type(rupture)})", "ERROR")
                        return False
                    
                    if isinstance(niveau_bas, int) and niveau_bas >= 0:
                        self.log(f"✅ Champ 'niveau_bas' est un entier >= 0: {niveau_bas}")
                    else:
                        self.log(f"❌ Champ 'niveau_bas' invalide: {niveau_bas} (type: {type(niveau_bas)})", "ERROR")
                        return False
                    
                    return True
                else:
                    self.log("❌ Réponse ne contient pas les champs requis 'rupture' et 'niveau_bas'", "ERROR")
                    self.log(f"Réponse reçue: {self.stats_data}", "ERROR")
                    return False
            else:
                self.log(f"❌ Endpoint /api/inventory/stats échoué - Status: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Request failed - Error: {str(e)}", "ERROR")
            return False
    
    def test_validate_calculations(self):
        """TEST 3: Valider les calculs en comparant avec les données d'inventaire"""
        self.log("🧪 TEST 3: Validation des calculs de statistiques")
        
        if not self.inventory_data or not self.stats_data:
            self.log("❌ Données d'inventaire ou de stats manquantes", "ERROR")
            return False
        
        try:
            # Calculer manuellement les statistiques à partir des données d'inventaire
            expected_rupture = 0
            expected_niveau_bas = 0
            
            for item in self.inventory_data:
                quantite = item.get('quantite', 0)
                quantite_min = item.get('quantiteMin', 0)
                
                if quantite <= 0:
                    expected_rupture += 1
                elif quantite <= quantite_min:
                    expected_niveau_bas += 1
            
            # Comparer avec les résultats de l'endpoint
            actual_rupture = self.stats_data.get('rupture')
            actual_niveau_bas = self.stats_data.get('niveau_bas')
            
            self.log("📊 Comparaison des calculs:")
            self.log(f"   Rupture - Attendu: {expected_rupture}, Reçu: {actual_rupture}")
            self.log(f"   Niveau bas - Attendu: {expected_niveau_bas}, Reçu: {actual_niveau_bas}")
            
            # Vérifier la correspondance
            if actual_rupture == expected_rupture:
                self.log("✅ Calcul 'rupture' correct")
            else:
                self.log(f"❌ Calcul 'rupture' incorrect - Attendu: {expected_rupture}, Reçu: {actual_rupture}", "ERROR")
                return False
            
            if actual_niveau_bas == expected_niveau_bas:
                self.log("✅ Calcul 'niveau_bas' correct")
            else:
                self.log(f"❌ Calcul 'niveau_bas' incorrect - Attendu: {expected_niveau_bas}, Reçu: {actual_niveau_bas}", "ERROR")
                return False
            
            # Vérifier le total des alertes
            total_expected = expected_rupture + expected_niveau_bas
            total_actual = actual_rupture + actual_niveau_bas
            
            self.log(f"📊 Total alertes - Attendu: {total_expected}, Reçu: {total_actual}")
            
            if total_actual == total_expected:
                self.log("✅ Total des alertes correct")
                return True
            else:
                self.log(f"❌ Total des alertes incorrect", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur lors de la validation - Error: {str(e)}", "ERROR")
            return False

    def test_detailed_analysis(self):
        """TEST 4: Analyse détaillée des articles par catégorie"""
        self.log("🧪 TEST 4: Analyse détaillée des articles par catégorie")
        
        if not self.inventory_data:
            self.log("❌ Données d'inventaire manquantes", "ERROR")
            return False
        
        try:
            self.log("📋 Analyse détaillée des articles d'inventaire:")
            
            rupture_items = []
            niveau_bas_items = []
            normal_items = []
            
            for item in self.inventory_data:
                quantite = item.get('quantite', 0)
                quantite_min = item.get('quantiteMin', 0)
                nom = item.get('nom', 'N/A')
                code = item.get('code', 'N/A')
                
                if quantite <= 0:
                    rupture_items.append({
                        'nom': nom,
                        'code': code,
                        'quantite': quantite,
                        'quantiteMin': quantite_min
                    })
                elif quantite <= quantite_min:
                    niveau_bas_items.append({
                        'nom': nom,
                        'code': code,
                        'quantite': quantite,
                        'quantiteMin': quantite_min
                    })
                else:
                    normal_items.append({
                        'nom': nom,
                        'code': code,
                        'quantite': quantite,
                        'quantiteMin': quantite_min
                    })
            
            self.log(f"📊 ARTICLES EN RUPTURE ({len(rupture_items)}):")
            for item in rupture_items[:5]:  # Afficher les 5 premiers
                self.log(f"   - {item['nom']} (Code: {item['code']}, Qté: {item['quantite']})")
            if len(rupture_items) > 5:
                self.log(f"   ... et {len(rupture_items) - 5} autres")
            
            self.log(f"📊 ARTICLES NIVEAU BAS ({len(niveau_bas_items)}):")
            for item in niveau_bas_items[:5]:  # Afficher les 5 premiers
                self.log(f"   - {item['nom']} (Code: {item['code']}, Qté: {item['quantite']}, Min: {item['quantiteMin']})")
            if len(niveau_bas_items) > 5:
                self.log(f"   ... et {len(niveau_bas_items) - 5} autres")
            
            self.log(f"📊 ARTICLES NORMAUX: {len(normal_items)}")
            
            # Vérifier que les calculs correspondent aux stats
            if (len(rupture_items) == self.stats_data.get('rupture') and 
                len(niveau_bas_items) == self.stats_data.get('niveau_bas')):
                self.log("✅ Analyse détaillée cohérente avec les statistiques")
                return True
            else:
                self.log("❌ Incohérence entre l'analyse détaillée et les statistiques", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur lors de l'analyse - Error: {str(e)}", "ERROR")
            return False
    
    def cleanup_test_data(self):
        """Nettoyer les données de test créées"""
        self.log("🧹 Nettoyage des données de test...")
        
        # Note: Pas de nettoyage spécifique nécessaire pour ce test
        # Les tests sont en lecture seule
        self.log("✅ Nettoyage terminé (tests en lecture seule)")
    
    def run_inventory_stats_tests(self):
        """Run comprehensive tests for Parts Used System in Work Orders"""
        self.log("=" * 80)
        self.log("TESTING SYSTÈME DE PIÈCES UTILISÉES DANS LES ORDRES DE TRAVAIL")
        self.log("=" * 80)
        self.log("CONTEXTE:")
        self.log("Test complet du système permettant d'ajouter des pièces utilisées lors des interventions.")
        self.log("Les pièces doivent être déduites de l'inventaire automatiquement et l'historique doit être conservé.")
        self.log("")
        self.log("SCÉNARIOS DE TEST:")
        self.log("1. 📦 Vérifier l'état initial (inventaire, ordres de travail, équipements)")
        self.log("2. 🔧 Test d'ajout de pièces avec commentaire")
        self.log("3. ✅ Vérifications après ajout (déduction inventaire)")
        self.log("4. 📋 Vérifier mise à jour ordre de travail")
        self.log("5. 🌐 Test avec pièce externe (texte libre)")
        self.log("6. 📊 Test d'ajout multiple de pièces")
        self.log("7. 📋 Vérification du journal d'audit")
        self.log("=" * 80)
        
        results = {
            "admin_login": False,
            "get_initial_state": False,
            "add_parts_with_comment": False,
            "verify_inventory_deduction": False,
            "verify_work_order_update": False,
            "external_parts": False,
            "multiple_parts_addition": False,
            "verify_audit_journal": False
        }
        
        # Test 1: Admin Login
        results["admin_login"] = self.test_admin_login()
        
        if not results["admin_login"]:
            self.log("❌ Cannot proceed with other tests - Admin login failed", "ERROR")
            return results
        
        # TESTS CRITIQUES DU SYSTÈME DE PIÈCES UTILISÉES
        self.log("\n" + "=" * 60)
        self.log("🔧 TESTS CRITIQUES - SYSTÈME DE PIÈCES UTILISÉES")
        self.log("=" * 60)
        
        # Test 1: Vérifier l'état initial
        results["get_initial_state"] = self.test_get_initial_state()
        
        # Test 2: Ajouter des pièces avec commentaire
        results["add_parts_with_comment"] = self.test_add_parts_with_comment()
        
        # Test 3: Vérifier la déduction d'inventaire
        results["verify_inventory_deduction"] = self.test_verify_inventory_deduction()
        
        # Test 4: Vérifier la mise à jour de l'ordre de travail
        results["verify_work_order_update"] = self.test_verify_work_order_update()
        
        # Test 5: Test avec pièce externe
        results["external_parts"] = self.test_external_parts()
        
        # Test 6: Test d'ajout multiple
        results["multiple_parts_addition"] = self.test_multiple_parts_addition()
        
        # Test 7: Vérifier le journal d'audit
        results["verify_audit_journal"] = self.test_verify_audit_journal()
        
        # Summary
        self.log("=" * 80)
        self.log("SYSTÈME DE PIÈCES UTILISÉES - RÉSULTATS DES TESTS")
        self.log("=" * 80)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        self.log(f"\n📊 Overall: {passed}/{total} tests passed")
        
        # Analyse détaillée des tests critiques
        critical_tests = ["get_initial_state", "add_parts_with_comment", "verify_inventory_deduction", 
                         "verify_work_order_update", "external_parts", "multiple_parts_addition", "verify_audit_journal"]
        critical_passed = sum(results.get(test, False) for test in critical_tests)
        
        self.log("\n" + "=" * 60)
        self.log("ANALYSE CRITIQUE DU SYSTÈME DE PIÈCES UTILISÉES")
        self.log("=" * 60)
        
        # TEST CRITIQUE 1: État initial
        if results.get("get_initial_state", False):
            self.log("🎉 TEST CRITIQUE 1 - ÉTAT INITIAL: ✅ SUCCÈS")
            self.log("✅ Inventaire, ordres de travail et équipements accessibles")
            self.log("✅ Données de test préparées")
        else:
            self.log("🚨 TEST CRITIQUE 1 - ÉTAT INITIAL: ❌ ÉCHEC")
            self.log("❌ Impossible d'accéder aux données de base")
        
        # TEST CRITIQUE 2: Ajout de pièces
        if results.get("add_parts_with_comment", False):
            self.log("🎉 TEST CRITIQUE 2 - AJOUT PIÈCES: ✅ SUCCÈS")
            self.log("✅ POST /api/work-orders/{id}/comments avec parts_used fonctionne")
            self.log("✅ Pièces correctement ajoutées avec commentaire")
        else:
            self.log("🚨 TEST CRITIQUE 2 - AJOUT PIÈCES: ❌ ÉCHEC")
            self.log("❌ Erreur lors de l'ajout de pièces")
        
        # TEST CRITIQUE 3: Déduction inventaire
        if results.get("verify_inventory_deduction", False):
            self.log("🎉 TEST CRITIQUE 3 - DÉDUCTION INVENTAIRE: ✅ SUCCÈS")
            self.log("✅ Déduction automatique du stock pour pièces d'inventaire")
            self.log("✅ Quantités correctement mises à jour")
        else:
            self.log("🚨 TEST CRITIQUE 3 - DÉDUCTION INVENTAIRE: ❌ ÉCHEC")
            self.log("❌ Déduction automatique ne fonctionne pas")
        
        # TEST CRITIQUE 4: Mise à jour ordre de travail
        if results.get("verify_work_order_update", False):
            self.log("🎉 TEST CRITIQUE 4 - MISE À JOUR ORDRE: ✅ SUCCÈS")
            self.log("✅ Historique complet conservé dans work_order.parts_used")
            self.log("✅ Toutes les informations présentes (timestamp, noms, quantités, sources)")
        else:
            self.log("🚨 TEST CRITIQUE 4 - MISE À JOUR ORDRE: ❌ ÉCHEC")
            self.log("❌ Historique des pièces non conservé")
        
        # TEST CRITIQUE 5: Pièces externes
        if results.get("external_parts", False):
            self.log("🎉 TEST CRITIQUE 5 - PIÈCES EXTERNES: ✅ SUCCÈS")
            self.log("✅ Pas de déduction pour pièces externes (texte libre)")
            self.log("✅ Pièces externes correctement enregistrées")
        else:
            self.log("🚨 TEST CRITIQUE 5 - PIÈCES EXTERNES: ❌ ÉCHEC")
            self.log("❌ Gestion des pièces externes incorrecte")
        
        # TEST CRITIQUE 6: Ajout multiple
        if results.get("multiple_parts_addition", False):
            self.log("🎉 TEST CRITIQUE 6 - AJOUT MULTIPLE: ✅ SUCCÈS")
            self.log("✅ Ajout de plusieurs pièces simultanément")
            self.log("✅ Toutes les pièces enregistrées et déductions correctes")
        else:
            self.log("🚨 TEST CRITIQUE 6 - AJOUT MULTIPLE: ❌ ÉCHEC")
            self.log("❌ Problème avec l'ajout multiple de pièces")
        
        # TEST CRITIQUE 7: Journal d'audit
        if results.get("verify_audit_journal", False):
            self.log("🎉 TEST CRITIQUE 7 - JOURNAL D'AUDIT: ✅ SUCCÈS")
            self.log("✅ Journal d'audit mis à jour")
            self.log("✅ Logs contiennent 'pièce(s) utilisée(s)'")
        else:
            self.log("🚨 TEST CRITIQUE 7 - JOURNAL D'AUDIT: ❌ ÉCHEC")
            self.log("❌ Journal d'audit non mis à jour")
        
        # Conclusion finale
        self.log("\n" + "=" * 80)
        self.log("CONCLUSION FINALE - SYSTÈME DE PIÈCES UTILISÉES")
        self.log("=" * 80)
        
        if critical_passed == len(critical_tests):
            self.log("🎉 SYSTÈME DE PIÈCES UTILISÉES ENTIÈREMENT FONCTIONNEL!")
            self.log("✅ Déduction automatique du stock pour pièces d'inventaire")
            self.log("✅ Pas de déduction pour pièces externes (texte libre)")
            self.log("✅ Historique complet conservé dans work_order.parts_used")
            self.log("✅ Toutes les informations présentes (timestamp, noms, quantités, sources)")
            self.log("✅ Journal d'audit mis à jour")
            self.log("✅ POST /api/work-orders/{id}/comments avec parts_used fonctionnel")
            self.log("✅ Support des pièces d'inventaire et externes")
            self.log("✅ Ajout multiple de pièces supporté")
            self.log("✅ Le système est PRÊT POUR PRODUCTION")
        else:
            self.log("⚠️ SYSTÈME DE PIÈCES UTILISÉES INCOMPLET - PROBLÈMES DÉTECTÉS")
            failed_critical = [test for test in critical_tests if not results.get(test, False)]
            self.log(f"❌ Tests critiques échoués: {', '.join(failed_critical)}")
            self.log("❌ Le système de pièces utilisées ne fonctionne pas correctement")
            self.log("❌ Intervention requise avant mise en production")
        
        return results

if __name__ == "__main__":
    tester = PartsUsedSystemTester()
    results = tester.run_parts_used_system_tests()
    
    # Exit with appropriate code
    critical_tests = [
        "admin_login", "get_initial_state", "add_parts_with_comment", 
        "verify_inventory_deduction", "verify_work_order_update", "external_parts", 
        "multiple_parts_addition", "verify_audit_journal"
    ]
    
    critical_passed = sum(results.get(test, False) for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        exit(0)  # Success
    else:
        exit(1)  # Failure
