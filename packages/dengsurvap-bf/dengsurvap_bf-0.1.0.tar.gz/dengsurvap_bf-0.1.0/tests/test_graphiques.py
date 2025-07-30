#!/usr/bin/env python3
"""
Script de test pour la fonctionnalité des graphiques de la fonction resume_display
"""

import sys
import os

# Ajouter le chemin du package dengsurvap-bf
current_dir = os.path.dirname(os.path.abspath(__file__))
dengsurvap_path = os.path.join(current_dir, 'dengsurvap-bf')
sys.path.insert(0, dengsurvap_path)

from dengsurvab import AppiClient
import requests

# Configuration du client
client = AppiClient("https://api-bf-dengue-survey-production.up.railway.app/")

print("🔧 TEST DE LA FONCTIONNALITÉ GRAPHIQUES")
print("=" * 50)

# Test de l'authentification
print("1. Authentification...")
try:
    auth_result = client.authenticate("admin@gmail.com", "admin123")
    print(f"   Authentification: {'✅ Succès' if auth_result.get('success') else '❌ Échec'}")
except Exception as e:
    print(f"   ❌ Erreur d'authentification: {e}")
    print("   Tentative avec des identifiants alternatifs...")
    
    # Essayer avec d'autres identifiants possibles
    try:
        auth_result = client.authenticate("admin", "admin")
        print(f"   Authentification: {'✅ Succès' if auth_result.get('success') else '❌ Échec'}")
    except Exception as e2:
        print(f"   ❌ Échec avec identifiants alternatifs: {e2}")
        auth_result = {"success": False}

if auth_result.get('success'):
    print("\n2. Test de la fonction resume_display avec graphiques...")
    print("   Note: Les graphiques s'afficheront dans une fenêtre séparée")
    
    try:
        # Test avec graphiques
        client.resume_display(verbose=True, show_details=True, graph=True)
        print("   ✅ Test des graphiques terminé")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test des graphiques: {e}")
    
    print("\n3. Test de la fonction resume_display sans graphiques...")
    try:
        # Test sans graphiques
        client.resume_display(verbose=True, show_details=True, graph=False)
        print("   ✅ Test sans graphiques terminé")
        
    except Exception as e:
        print(f"   ❌ Erreur lors du test sans graphiques: {e}")

else:
    print("❌ Impossible de tester les graphiques sans authentification")

print("\n4. Déconnexion...")
print(client.logout()) 