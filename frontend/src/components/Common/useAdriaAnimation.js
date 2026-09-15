import { useEffect, useRef, useState } from 'react';

// Jeux de sprites par personnage : "base" = image par defaut deja utilisee
// partout dans l'appli (yeux ouverts, bouche ouverte). Un personnage sans
// entree ici reste sur son image fixe (juste le balancement, pas d'animation
// du visage) - voir ADRIA_AVATARS.available dans AdriaAvatar.jsx.
const FRAMES = {
  cle: {
    base: '/assets/adria/cle.png',
    mouthClosed: '/assets/adria/cle_bouche_fermee.png',
    eyesClosed: '/assets/adria/cle_yeux_fermes.png',
    both: '/assets/adria/cle_bouche_yeux_fermes.png',
  },
  'cle-fille': {
    base: '/assets/adria/cle-fille.png',
    mouthClosed: '/assets/adria/cle-fille_bouche_fermee.png',
    eyesClosed: '/assets/adria/cle-fille_yeux_fermes.png',
    both: '/assets/adria/cle-fille_bouche_yeux_fermes.png',
  },
};

export const hasSpriteFrames = (avatarId) => Boolean(FRAMES[avatarId]);

function frameFor(avatarId, mouthOpen, eyesOpen, fallbackSrc) {
  const f = FRAMES[avatarId];
  if (!f) return fallbackSrc;
  if (mouthOpen && eyesOpen) return f.base;
  if (!mouthOpen && eyesOpen) return f.mouthClosed || f.base;
  if (mouthOpen && !eyesOpen) return f.eyesClosed || f.base;
  return f.both || f.mouthClosed || f.eyesClosed || f.base;
}

/**
 * Anime un personnage Adria par echange d'images (comme l'assistant Office) :
 * clignement des yeux permanent et aleatoire, levres qui bougent tant que
 * `speaking` est vrai. Retombe sur `fallbackSrc` (image fixe) pour les
 * personnages sans jeu de sprites.
 */
export function useAdriaAnimation(avatarId, fallbackSrc, speaking) {
  const [mouthOpen, setMouthOpen] = useState(true);
  const [eyesOpen, setEyesOpen] = useState(true);
  const preloadedRef = useRef(new Set());
  const animated = hasSpriteFrames(avatarId);

  // Precharge les variantes en memoire des qu'un personnage anime est actif,
  // pour eviter le "rien ne se passe" le temps du premier telechargement.
  useEffect(() => {
    const f = FRAMES[avatarId];
    if (!f) return;
    Object.values(f).forEach((src) => {
      if (preloadedRef.current.has(src)) return;
      preloadedRef.current.add(src);
      const img = new Image();
      img.src = src;
    });
  }, [avatarId]);

  // Reinitialise l'expression au changement de personnage.
  useEffect(() => {
    setMouthOpen(true);
    setEyesOpen(true);
  }, [avatarId]);

  // Clignement independant, toutes les 2.6 a 5.2s.
  useEffect(() => {
    if (!animated) return undefined;
    let closeTimer;
    let scheduleTimer;
    const scheduleBlink = () => {
      const delay = 2600 + Math.random() * 2600;
      scheduleTimer = setTimeout(() => {
        setEyesOpen(false);
        closeTimer = setTimeout(() => {
          setEyesOpen(true);
          scheduleBlink();
        }, 160);
      }, delay);
    };
    scheduleBlink();
    return () => {
      clearTimeout(scheduleTimer);
      clearTimeout(closeTimer);
    };
  }, [animated, avatarId]);

  // Levres qui bougent tant que `speaking` est vrai.
  useEffect(() => {
    if (!animated || !speaking) {
      setMouthOpen(true);
      return undefined;
    }
    const interval = setInterval(() => {
      setMouthOpen((m) => !m);
    }, 150 + Math.random() * 90);
    return () => clearInterval(interval);
  }, [animated, speaking, avatarId]);

  return frameFor(avatarId, mouthOpen, eyesOpen, fallbackSrc);
}
