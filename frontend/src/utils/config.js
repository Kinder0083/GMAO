/**
 * Configuration universelle de l'URL backend
 * Fonctionne automatiquement en local ET à distance avec Proxmox
 * - Si REACT_APP_BACKEND_URL est défini → utilise cette URL
 * - Sinon → utilise window.location (hostname) + port 8001
 * 
 * Exemples :
 * - Accès local : http://192.168.1.124:3000 → API sur http://192.168.1.124:8001/api
 * - Accès distant : http://82.66.41.98:3000 → API sur http://82.66.41.98:8001/api
 * - Nom de domaine : http://mon-domaine.com:3000 → API sur http://mon-domaine.com:8001/api
 */
export const getBackendURL = () => {
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // Construire l'URL backend avec le port 8001
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}:8001`;
};

export const BACKEND_URL = getBackendURL();
