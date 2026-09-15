import React from 'react';

// Catalogue des personnages disponibles pour l'assistant IA. Chaque entree
// est { id, label, color } - la couleur sert a la fois de fond d'avatar et
// de teinte d'accent (bouton, bulle de chat) quand ce personnage est choisi.
export const ADRIA_AVATARS = [
  { id: 'robot', label: 'Robot', color: '#7c3aed' },
  { id: 'robot-tech', label: 'Robot Technicien', color: '#ea580c' },
  { id: 'renard', label: 'Renard', color: '#f59e0b' },
  { id: 'chouette', label: 'Chouette', color: '#4338ca' },
  { id: 'chat', label: 'Chat', color: '#0d9488' },
  { id: 'abeille', label: 'Abeille', color: '#eab308' },
];

export const DEFAULT_AVATAR = 'robot';

export const getAvatarColor = (variant) =>
  ADRIA_AVATARS.find((a) => a.id === variant)?.color || ADRIA_AVATARS[0].color;

const Face = ({ variant }) => {
  switch (variant) {
    case 'robot-tech':
      return (
        <>
          <rect x="10" y="14" width="20" height="15" rx="5" fill="#fff" />
          <circle cx="16" cy="21.5" r="1.8" fill="#ea580c" />
          <circle cx="24" cy="21.5" r="1.8" fill="#ea580c" />
          <rect x="15" y="25.5" width="10" height="2" rx="1" fill="#ea580c" />
          {/* Casque de chantier */}
          <path d="M9 14 a11 8 0 0 1 22 0 z" fill="#facc15" />
          <rect x="7.5" y="12.5" width="25" height="3" rx="1.5" fill="#facc15" />
        </>
      );
    case 'renard':
      return (
        <>
          <path d="M11 14 L16 8 L19 15 Z" fill="#fff" />
          <path d="M29 14 L24 8 L21 15 Z" fill="#fff" />
          <path d="M13 15 a7 7 0 0 0 14 0 a7 9 0 0 1 -14 0 z" fill="#fff" />
          <path d="M20 22 L17 26 L23 26 Z" fill="#fff" />
          <circle cx="20" cy="26" r="1" fill="#7c3f00" />
          <circle cx="16" cy="17" r="1.4" fill="#7c3f00" />
          <circle cx="24" cy="17" r="1.4" fill="#7c3f00" />
        </>
      );
    case 'chouette':
      return (
        <>
          <path d="M13 9 L15 13 L11 13 Z" fill="#fff" />
          <path d="M27 9 L29 13 L25 13 Z" fill="#fff" />
          <circle cx="15" cy="19" r="6" fill="#fff" />
          <circle cx="25" cy="19" r="6" fill="#fff" />
          <circle cx="15" cy="19" r="2.6" fill="#312e81" />
          <circle cx="25" cy="19" r="2.6" fill="#312e81" />
          <path d="M18.5 22 L20 25 L21.5 22 Z" fill="#f59e0b" />
        </>
      );
    case 'chat':
      return (
        <>
          <path d="M11 15 L14 7 L18 14 Z" fill="#fff" />
          <path d="M29 15 L26 7 L22 14 Z" fill="#fff" />
          <circle cx="20" cy="20" r="9" fill="#fff" />
          <path d="M15 19 a1.6 2 0 1 0 0.1 0" fill="#134e4a" />
          <path d="M25 19 a1.6 2 0 1 0 0.1 0" fill="#134e4a" />
          <path d="M20 22 L18.5 23.5 L21.5 23.5 Z" fill="#f472b6" />
          <line x1="4" y1="21" x2="12" y2="20" stroke="#fff" strokeWidth="1" />
          <line x1="4" y1="24" x2="12" y2="23" stroke="#fff" strokeWidth="1" />
          <line x1="36" y1="21" x2="28" y2="20" stroke="#fff" strokeWidth="1" />
          <line x1="36" y1="24" x2="28" y2="23" stroke="#fff" strokeWidth="1" />
        </>
      );
    case 'abeille':
      return (
        <>
          <path d="M14 10 Q10 6 8 10" stroke="#422006" strokeWidth="1.4" fill="none" strokeLinecap="round" />
          <path d="M26 10 Q30 6 32 10" stroke="#422006" strokeWidth="1.4" fill="none" strokeLinecap="round" />
          <circle cx="8" cy="10" r="1.3" fill="#422006" />
          <circle cx="32" cy="10" r="1.3" fill="#422006" />
          <circle cx="20" cy="21" r="10" fill="#fffbea" />
          <circle cx="16" cy="19" r="3" fill="#1c1917" />
          <circle cx="24" cy="19" r="3" fill="#1c1917" />
          <circle cx="15" cy="18" r="1" fill="#fff" />
          <circle cx="23" cy="18" r="1" fill="#fff" />
          <path d="M16 25 Q20 28 24 25" stroke="#1c1917" strokeWidth="1.4" fill="none" strokeLinecap="round" />
        </>
      );
    case 'robot':
    default:
      return (
        <>
          <line x1="20" y1="6" x2="20" y2="11" stroke="#fff" strokeWidth="1.6" />
          <circle cx="20" cy="5" r="1.6" fill="#fff" />
          <rect x="10" y="11" width="20" height="17" rx="6" fill="#fff" />
          <circle cx="16" cy="19.5" r="2" fill="#7c3aed" />
          <circle cx="24" cy="19.5" r="2" fill="#7c3aed" />
          <rect x="15" y="24" width="10" height="2" rx="1" fill="#7c3aed" />
        </>
      );
  }
};

/**
 * Avatar circulaire de l'assistant IA - fond colore + traits du personnage
 * choisi par l'utilisateur (Personnalisation > Assistant IA). `variant`
 * accepte un id de ADRIA_AVATARS ; toute valeur inconnue retombe sur 'robot'.
 */
const AdriaAvatar = ({ variant = DEFAULT_AVATAR, size = 32, className = '' }) => {
  const color = getAvatarColor(variant);
  return (
    <svg
      viewBox="0 0 40 40"
      width={size}
      height={size}
      className={className}
      role="img"
      aria-label="Avatar de l'assistant IA"
    >
      <circle cx="20" cy="20" r="20" fill={color} />
      <Face variant={variant} />
    </svg>
  );
};

export default AdriaAvatar;
