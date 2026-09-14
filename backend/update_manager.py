"""
Gestionnaire de mise à jour FSAO Iris
"""
import os
import subprocess
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List
import aiohttp
from pathlib import Path

class UpdateManager:
    def __init__(self, db):
        self.db = db
        self.github_user = os.environ.get("GITHUB_USER", "Kinder0083")
        self.github_repo = os.environ.get("GITHUB_REPO", "GMAO")
        self.github_branch = os.environ.get("GITHUB_BRANCH", "main")
        # Centraliser le chemin de l'application
        self.app_root = str(Path(__file__).parent.parent)
        self.current_commit = None
        self._load_version()
    
    def _load_version(self):
        """Charge la version depuis updates/version.json"""
        try:
            # Chercher version.json dans plusieurs emplacements
            for base in [Path(self.app_root), Path("/opt/gmao-iris")]:
                vf = base / "updates" / "version.json"
                if vf.exists():
                    with open(vf) as f:
                        data = json.load(f)
                    self.current_version = data.get("version", "1.5.0")
                    return
        except Exception:
            pass
        self.current_version = "1.5.0"
        
    async def get_current_version(self) -> str:
        """Récupère la version actuelle depuis version.json"""
        self._load_version()
        return self.current_version
    
    async def get_current_commit(self) -> Optional[str]:
        """Récupère le commit actuel depuis git"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.app_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()[:7]
        except:
            pass
        return None
    
    @staticmethod
    def _parse_semver(v: str):
        parts = []
        for p in (v or "").split('.'):
            num = ''
            for ch in p:
                if ch.isdigit():
                    num += ch
                else:
                    break
            parts.append(int(num) if num else 0)
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])

    @classmethod
    def _compare_versions(cls, v1: str, v2: str) -> int:
        t1, t2 = cls._parse_semver(v1), cls._parse_semver(v2)
        if t1 > t2:
            return 1
        if t1 < t2:
            return -1
        return 0

    async def check_github_version(self) -> Optional[Dict]:
        """
        Vérifie la dernière version disponible sur GitHub.

        Source de vérité : updates/version.json (via raw.githubusercontent.com),
        comparé en versioning sémantique — PAS l'API api.github.com/repos/.../commits
        qui est limitée à 60 requêtes/heure par IP et peut donc échouer
        silencieusement (et faire croire à tort que l'app est à jour).
        Le SHA/date/message de commit ne sont récupérés qu'en best-effort,
        pour l'affichage, sans jamais bloquer la détection de mise à jour.
        """
        try:
            version_url = f"https://raw.githubusercontent.com/{self.github_user}/{self.github_repo}/{self.github_branch}/updates/version.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(version_url, timeout=aiohttp.ClientTimeout(total=8)) as vresp:
                    if vresp.status != 200:
                        return None
                    # raw.githubusercontent.com sert le JSON avec Content-Type: text/plain,
                    # donc content_type=None pour ne pas faire échouer le parsing aiohttp.
                    version_data = await vresp.json(content_type=None)

            remote_version = version_data.get("version", "")
            if not remote_version:
                return None

            self._load_version()
            update_available = self._compare_versions(remote_version, self.current_version) > 0

            remote_commit = None
            commit_date = version_data.get("releaseDate")
            commit_message = version_data.get("description", "")
            try:
                async with aiohttp.ClientSession() as session:
                    commit_url = f"https://api.github.com/repos/{self.github_user}/{self.github_repo}/commits/{self.github_branch}"
                    async with session.get(commit_url, timeout=aiohttp.ClientTimeout(total=5)) as cresp:
                        if cresp.status == 200:
                            commit_data = await cresp.json()
                            remote_commit = commit_data["sha"][:7]
                            commit_date = commit_data["commit"]["author"]["date"]
                            commit_message = commit_data["commit"]["message"].split('\n')[0]
            except Exception:
                pass  # quota GitHub atteint ou hors-ligne : on garde les infos de version.json

            local_commit = await self.get_current_commit()

            return {
                "version": remote_version,
                "versionName": version_data.get("versionName", ""),
                "commit": remote_commit,
                "date": commit_date,
                "message": commit_message,
                "available": update_available,
                "local_commit": local_commit,
                "changes": version_data.get("changes", [])
            }

        except Exception as e:
            print(f"Erreur vérification version GitHub: {e}")
            return None
    
    async def get_changelog(self, from_version: str = None) -> List[Dict]:
        """Récupère le changelog depuis GitHub"""
        try:
            # Chercher le fichier CHANGELOG.md
            url = f"https://raw.githubusercontent.com/{self.github_user}/{self.github_repo}/{self.github_branch}/CHANGELOG.md"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        changelog_text = await response.text()
                        return self._parse_changelog(changelog_text, from_version)
            
            # Si pas de CHANGELOG, créer un changelog par défaut
            return [{
                "version": "latest",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": [
                    "✅ Corrections de bugs",
                    "✅ Améliorations de performance",
                    "✅ Mises à jour de sécurité"
                ]
            }]
                    
        except Exception as e:
            print(f"Erreur récupération changelog: {e}")
            return []
    
    def _parse_changelog(self, changelog_text: str, from_version: str = None) -> List[Dict]:
        """Parse le fichier CHANGELOG.md"""
        changelogs = []
        current_version = None
        current_changes = []
        
        for line in changelog_text.split('\n'):
            line = line.strip()
            
            # Détecter une nouvelle version (## [1.2.0] - 2024-10-20)
            if line.startswith('## '):
                if current_version and current_changes:
                    changelogs.append({
                        "version": current_version,
                        "changes": current_changes
                    })
                    if from_version and current_version == from_version:
                        break
                
                # Extraire version
                parts = line.split('[')
                if len(parts) > 1:
                    current_version = parts[1].split(']')[0]
                    current_changes = []
            
            # Détecter les changements (lignes commençant par - ou *)
            elif line.startswith(('-', '*', '•')) and current_version:
                change = line[1:].strip()
                if change:
                    current_changes.append(change)
        
        # Ajouter le dernier changelog
        if current_version and current_changes:
            changelogs.append({
                "version": current_version,
                "changes": current_changes
            })
        
        return changelogs
    
    async def get_update_history(self) -> List[Dict]:
        """Récupère l'historique des mises à jour depuis la DB"""
        try:
            history = await self.db.update_history.find().sort("date", -1).to_list(20)
            
            result = []
            for item in history:
                result.append({
                    "id": str(item["_id"]),
                    "version": item.get("version"),
                    "date": item.get("date"),
                    "status": item.get("status"),
                    "message": item.get("message", "")
                })
            
            return result
        except Exception as e:
            print(f"Erreur récupération historique: {e}")
            return []
    
    async def save_update_record(self, version: str, status: str, message: str = ""):
        """Enregistre une mise à jour dans l'historique"""
        try:
            await self.db.update_history.insert_one({
                "version": version,
                "date": datetime.now(),
                "status": status,
                "message": message
            })
        except Exception as e:
            print(f"Erreur sauvegarde historique: {e}")
    
    async def create_backup(self) -> Dict:
        """Crée un backup de la base de données"""
        try:
            backup_dir = Path(self.app_root) / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"
            
            # Exécuter mongodump
            cmd = [
                "mongodump",
                "--uri", os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
                "--db", os.environ.get('DB_NAME', 'gmao_iris'),
                "--out", str(backup_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "path": str(backup_path),
                    "timestamp": timestamp
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def apply_update(self, github_token: Optional[str] = None) -> Dict:
        """Lance le script de mise à jour"""
        try:
            # Créer un backup avant la mise à jour
            backup_result = await self.create_backup()
            if not backup_result["success"]:
                return {
                    "success": False,
                    "message": "Échec création backup",
                    "error": backup_result.get("error")
                }
            
            # Lancer le script de mise à jour
            script_path = f"{self.app_root}/scripts/update.sh"
            
            env = os.environ.copy()
            if github_token:
                env["GITHUB_TOKEN"] = github_token
            
            process = await asyncio.create_subprocess_exec(
                "bash", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                await self.save_update_record(
                    version="latest",
                    status="success",
                    message="Mise à jour appliquée avec succès"
                )
                
                return {
                    "success": True,
                    "message": "Mise à jour appliquée avec succès",
                    "output": stdout.decode(),
                    "backup_path": backup_result["path"]
                }
            else:
                await self.save_update_record(
                    version="latest",
                    status="failed",
                    message=f"Échec: {stderr.decode()[:200]}"
                )
                
                return {
                    "success": False,
                    "message": "Échec de la mise à jour",
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Erreur lors de la mise à jour",
                "error": str(e)
            }
    
    async def rollback_to_version(self, backup_path: str) -> Dict:
        """Restaure une version précédente depuis un backup"""
        try:
            # Vérifier que le backup existe
            if not Path(backup_path).exists():
                return {
                    "success": False,
                    "message": "Backup introuvable"
                }
            
            # Exécuter mongorestore
            cmd = [
                "mongorestore",
                "--uri", os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
                "--db", os.environ.get('DB_NAME', 'gmao_iris'),
                "--drop",
                str(Path(backup_path) / os.environ.get('DB_NAME', 'gmao_iris'))
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "message": "Rollback effectué avec succès"
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_git_history(self, limit: int = 20) -> List[Dict]:
        """Récupère l'historique des commits Git (versions précédentes)"""
        try:
            app_root = self.app_root
            
            # Vérifier si c'est un dépôt Git
            if not Path(f"{app_root}/.git").exists():
                return []
            
            # Obtenir le commit actuel
            current_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=app_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            current_commit = current_result.stdout.strip() if current_result.returncode == 0 else None
            
            # Obtenir l'historique des commits
            result = subprocess.run(
                ['git', 'log', f'--max-count={limit}', '--format=%H|%h|%ai|%s|%an'],
                cwd=app_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    full_hash, short_hash, date, message, author = parts
                    commits.append({
                        "id": full_hash,
                        "short_id": short_hash,
                        "date": date,
                        "message": message,
                        "author": author,
                        "is_current": full_hash == current_commit
                    })
            
            return commits
            
        except Exception as e:
            print(f"Erreur récupération historique Git: {e}")
            return []

    async def rollback_to_commit(self, commit_hash: str) -> Dict:
        """
        Lance un rollback Git vers un commit spécifique.

        Délègue à MAJ_FSAO.sh (même script robuste que la mise à jour normale :
        page de maintenance, backup MongoDB, réinstallation des dépendances,
        rebuild frontend, redémarrage du service) avec le commit visé comme
        3e argument, au lieu d'un simple `git reset --hard` en direct qui ne
        change que le code sur disque sans jamais réinstaller ni redémarrer
        quoi que ce soit.
        """
        import subprocess as sp
        import uuid

        app_root = self.app_root

        if not Path(f"{app_root}/.git").exists():
            return {
                "success": False,
                "message": "Pas de dépôt Git trouvé"
            }

        script_path = Path(app_root) / "MAJ_FSAO.sh"
        if not script_path.exists():
            return {
                "success": False,
                "message": f"Script de mise à jour introuvable: {script_path}"
            }

        update_id = str(uuid.uuid4())
        version_label = f"rollback-{commit_hash[:7]}"

        await self.save_update_record(
            version=version_label,
            status="in_progress",
            message=f"Rollback vers le commit {commit_hash[:7]} lancé"
        )
        await self.db.system_settings.update_one(
            {"key": "last_update_result"},
            {"$set": {
                "key": "last_update_result",
                "in_progress": True,
                "success": False,
                "history_id": update_id,
                "current_step": f"Lancement du rollback vers {commit_hash[:7]}",
                "status": "in_progress",
                "version_after": version_label,
                "updated_at": datetime.now().isoformat()
            }},
            upsert=True
        )

        try:
            sp.Popen(
                ["/bin/bash", str(script_path), version_label, update_id, commit_hash],
                stdout=open("/var/log/gmao-iris-update-launcher.log", "a"),
                stderr=sp.STDOUT,
                start_new_session=True,
                cwd=str(app_root)
            )
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur lancement du script de rollback: {e}"
            }

        return {
            "success": True,
            "accepted": True,
            "update_id": update_id,
            "message": f"Rollback vers {commit_hash[:7]} lancé. Le service va redémarrer automatiquement.",
            "needs_restart": True
        }
