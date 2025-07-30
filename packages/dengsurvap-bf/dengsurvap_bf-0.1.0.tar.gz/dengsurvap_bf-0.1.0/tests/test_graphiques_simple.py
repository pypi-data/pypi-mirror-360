#!/usr/bin/env python3
"""
Script de test simple pour la fonctionnalité des graphiques
sans authentification (pour tester les dépendances)
"""

import sys
import os

# Ajouter le chemin du package dengsurvap-bf
current_dir = os.path.dirname(os.path.abspath(__file__))
dengsurvap_path = os.path.join(current_dir, 'dengsurvap-bf')
sys.path.insert(0, dengsurvap_path)

def test_dependencies():
    """Test des dépendances pour les graphiques"""
    
    print("🔧 TEST DES DÉPENDANCES POUR LES GRAPHIQUES")
    print("=" * 50)
    
    # Test matplotlib
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib installé")
    except ImportError as e:
        print(f"❌ matplotlib non installé: {e}")
        return False
    
    # Test seaborn
    try:
        import seaborn as sns
        print("✅ seaborn installé")
    except ImportError as e:
        print(f"❌ seaborn non installé: {e}")
        return False
    
    # Test scipy
    try:
        from scipy import stats
        print("✅ scipy installé")
    except ImportError as e:
        print(f"❌ scipy non installé: {e}")
        return False
    
    # Test pandas
    try:
        import pandas as pd
        print("✅ pandas installé")
    except ImportError as e:
        print(f"❌ pandas non installé: {e}")
        return False
    
    # Test numpy
    try:
        import numpy as np
        print("✅ numpy installé")
    except ImportError as e:
        print(f"❌ numpy non installé: {e}")
        return False
    
    return True

def test_basic_plot():
    """Test de création d'un graphique simple"""
    
    print("\n📊 TEST DE CRÉATION D'UN GRAPHIQUE SIMPLE")
    print("-" * 40)
    
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        
        # Créer des données de test
        data = np.random.normal(0, 1, 1000)
        
        # Créer un histogramme simple
        plt.figure(figsize=(10, 6))
        plt.hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Test de Graphique - Distribution Normale', fontweight='bold')
        plt.xlabel('Valeur')
        plt.ylabel('Fréquence')
        plt.grid(True, alpha=0.3)
        
        # Ajouter des statistiques
        mean_val = np.mean(data)
        std_val = np.std(data)
        plt.text(0.02, 0.98, f'Moyenne: {mean_val:.2f}\nÉcart-type: {std_val:.2f}', 
                transform=plt.gca().transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Graphique de test créé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du graphique: {e}")
        return False

def test_seaborn_plot():
    """Test de création d'un graphique avec seaborn"""
    
    print("\n🎨 TEST DE CRÉATION D'UN GRAPHIQUE AVEC SEABORN")
    print("-" * 50)
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd
        import numpy as np
        
        # Configuration du style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Créer des données de test
        np.random.seed(42)
        data = pd.DataFrame({
            'age': np.random.normal(35, 15, 1000),
            'region': np.random.choice(['Region A', 'Region B', 'Region C', 'Region D'], 1000),
            'issue': np.random.choice(['Cas', 'Décès', 'Guérison'], 1000, p=[0.7, 0.1, 0.2])
        })
        
        # Créer une figure avec plusieurs sous-graphiques
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Test de Graphiques Seaborn - Données de Test', 
                    fontsize=16, fontweight='bold')
        
        # Graphique 1: Distribution des âges
        sns.histplot(data=data, x='age', bins=20, ax=ax1, color='skyblue')
        ax1.set_title('Distribution des Âges', fontweight='bold')
        ax1.set_xlabel('Âge')
        ax1.set_ylabel('Fréquence')
        
        # Graphique 2: Répartition par région
        region_counts = data['region'].value_counts()
        sns.barplot(x=region_counts.index, y=region_counts.values, ax=ax2, palette='Set3')
        ax2.set_title('Répartition par Région', fontweight='bold')
        ax2.set_xlabel('Région')
        ax2.set_ylabel('Nombre de cas')
        ax2.tick_params(axis='x', rotation=45)
        
        # Graphique 3: Répartition des issues
        issue_counts = data['issue'].value_counts()
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(issue_counts)))
        wedges, texts, autotexts = ax3.pie(issue_counts.values, labels=issue_counts.index, 
                                           autopct='%1.1f%%', colors=colors, startangle=90)
        ax3.set_title('Répartition des Issues', fontweight='bold')
        
        # Graphique 4: Box plot des âges par issue
        sns.boxplot(data=data, x='issue', y='age', ax=ax4, palette='Set2')
        ax4.set_title('Âge par Issue', fontweight='bold')
        ax4.set_xlabel('Issue')
        ax4.set_ylabel('Âge')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ Graphiques Seaborn créés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des graphiques Seaborn: {e}")
        return False

def main():
    """Fonction principale de test"""
    
    print("🚀 DÉMARRAGE DES TESTS DE GRAPHIQUES")
    print("=" * 50)
    
    # Test 1: Dépendances
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dépendances manquantes. Installez-les avec:")
        print("   pip install matplotlib seaborn scipy pandas numpy")
        return
    
    # Test 2: Graphique simple
    simple_ok = test_basic_plot()
    
    # Test 3: Graphiques Seaborn
    seaborn_ok = test_seaborn_plot()
    
    # Résumé
    print("\n📋 RÉSUMÉ DES TESTS")
    print("=" * 30)
    print(f"Dépendances: {'✅ OK' if deps_ok else '❌ ÉCHEC'}")
    print(f"Graphique simple: {'✅ OK' if simple_ok else '❌ ÉCHEC'}")
    print(f"Graphiques Seaborn: {'✅ OK' if seaborn_ok else '❌ ÉCHEC'}")
    
    if deps_ok and simple_ok and seaborn_ok:
        print("\n🎉 Tous les tests de graphiques sont réussis !")
        print("   La fonctionnalité resume_display avec graph=True devrait fonctionner.")
    else:
        print("\n⚠️  Certains tests ont échoué.")
        print("   Vérifiez l'installation des dépendances.")

if __name__ == "__main__":
    main() 