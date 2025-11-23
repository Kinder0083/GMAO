#!/usr/bin/env python3
"""
Script pour importer le contenu complet du manuel dans MongoDB
"""
import asyncio
import json
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import uuid

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def import_manual():
    """Importer le contenu du manuel depuis le fichier JSON"""
    
    # Connexion à MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.gmao_iris
    
    print("📚 Importation du manuel utilisateur...")
    
    try:
        # Charger le fichier JSON
        with open('manual_content_complete.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Fichier chargé : Version {data['version']}")
        print(f"📖 {len(data['chapters'])} chapitres")
        print(f"📄 {len(data['sections'])} sections")
        
        # Supprimer l'ancien contenu
        print("\n🗑️  Suppression de l'ancien contenu...")
        await db.manual_versions.delete_many({})
        await db.manual_chapters.delete_many({})
        await db.manual_sections.delete_many({})
        print("✅ Ancien contenu supprimé")
        
        # Créer la nouvelle version
        print(f"\n📝 Création de la version {data['version']}...")
        now = datetime.now(timezone.utc)
        version = {
            "id": str(uuid.uuid4()),
            "version": data['version'],
            "release_date": now.isoformat(),
            "changes": data['changes'],
            "author_id": "system",
            "author_name": "Système",
            "is_current": True
        }
        await db.manual_versions.insert_one(version)
        print("✅ Version créée")
        
        # Insérer les chapitres
        print(f"\n📚 Insertion des {len(data['chapters'])} chapitres...")
        for chapter in data['chapters']:
            chapter_data = {
                **chapter,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
            await db.manual_chapters.insert_one(chapter_data)
            print(f"  ✅ {chapter['title']}")
        
        # Insérer les sections
        print(f"\n📄 Insertion des {len(data['sections'])} sections...")
        for section in data['sections']:
            section_data = {
                **section,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "video_url": section.get("video_url"),
                "images": section.get("images", [])
            }
            await db.manual_sections.insert_one(section_data)
            print(f"  ✅ {section['title']}")
        
        print("\n" + "="*60)
        print("🎉 IMPORTATION TERMINÉE AVEC SUCCÈS !")
        print("="*60)
        print(f"\n📊 Résumé :")
        print(f"  • Version : {data['version']}")
        print(f"  • Chapitres : {len(data['chapters'])}")
        print(f"  • Sections : {len(data['sections'])}")
        print(f"  • Modifications : {len(data['changes'])}")
        print("\n✅ Le manuel est maintenant disponible dans l'application !\n")
        
    except FileNotFoundError:
        print("❌ Erreur : Fichier manual_content_complete.json introuvable")
        print("   Assurez-vous que le fichier existe dans le même répertoire")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}")
    except Exception as e:
        print(f"❌ Erreur lors de l'importation : {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(import_manual())
