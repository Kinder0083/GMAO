import React from 'react';

// Catalogue des personnages disponibles pour l'assistant IA. Chaque image
// vit dans public/assets/adria/<id>.png (fond transparent, portrait carre).
export const ADRIA_AVATARS = [
  { id: 'cle', label: 'Clé' },
  { id: 'chariot', label: 'Chariot élévateur' },
  { id: 'cafetiere', label: 'Cafetière' },
  { id: 'ampoule', label: 'Ampoule' },
  { id: 'voiture', label: 'Voiture' },
  { id: 'fusee', label: 'Fusée' },
];

export const DEFAULT_AVATAR = 'cle';

const isValidAvatar = (variant) => ADRIA_AVATARS.some((a) => a.id === variant);

/**
 * Avatar de l'assistant IA - photo du personnage choisi par l'utilisateur
 * (Personnalisation > Assistant IA). `variant` accepte un id de ADRIA_AVATARS ;
 * toute valeur inconnue (anciens avatars SVG "robot"/"renard"/... d'avant
 * cette version) retombe sur DEFAULT_AVATAR plutot que de casser l'affichage.
 */
const AdriaAvatar = ({ variant = DEFAULT_AVATAR, size = 32, className = '' }) => {
  const id = isValidAvatar(variant) ? variant : DEFAULT_AVATAR;
  return (
    <img
      src={`/assets/adria/${id}.png`}
      alt="Avatar de l'assistant IA"
      className={className}
      style={{
        width: size,
        height: size,
        objectFit: 'cover',
        objectPosition: '50% 32%',
        borderRadius: '50%',
        flexShrink: 0,
        display: 'block',
      }}
    />
  );
};

export default AdriaAvatar;
