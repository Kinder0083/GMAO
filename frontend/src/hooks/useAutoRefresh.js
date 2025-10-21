import { useEffect, useRef } from 'react';

/**
 * Hook personnalisé pour rafraîchir automatiquement des données toutes les 5 secondes
 * @param {Function} refreshFunction - Fonction à appeler pour rafraîchir les données
 * @param {Array} dependencies - Tableau de dépendances (comme dans useEffect)
 * @param {number} interval - Intervalle en millisecondes (par défaut 5000ms = 5s)
 */
export const useAutoRefresh = (refreshFunction, dependencies = [], interval = 5000) => {
  const intervalRef = useRef(null);

  useEffect(() => {
    // Appeler la fonction immédiatement
    refreshFunction();

    // Configurer le rafraîchissement automatique
    intervalRef.current = setInterval(() => {
      refreshFunction();
    }, interval);

    // Nettoyer l'intervalle au démontage
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, dependencies);
};

export default useAutoRefresh;
