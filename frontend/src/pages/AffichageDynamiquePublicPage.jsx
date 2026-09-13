import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { BACKEND_URL } from '../utils/config';
import BlockContent from '../components/AffichageDynamique/BlockRenderer';

const API = BACKEND_URL;
const DESIGN_W = 1920;
const DESIGN_H = 1080;
const REFRESH_MS = 30000;

// Page publique, sans authentification : lecture seule (aucun appel d'écriture ici).
// Destinée aux lecteurs de signalétique (Yodeck, OptiSigns, navigateur en kiosque, etc.)
export default function AffichageDynamiquePublicPage() {
  const { token } = useParams();
  const [screen, setScreen] = useState(null);
  const [error, setError] = useState(null);
  const [scale, setScale] = useState(1);
  const wrapperRef = useRef(null);

  const fetchScreen = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/affichage-dynamique/public/${token}`);
      if (res.ok) {
        const d = await res.json();
        setScreen(d);
        setError(null);
      } else if (res.status === 404) {
        setError('Lien invalide ou écran supprimé.');
      } else if (res.status === 403) {
        setError('Cet écran est désactivé.');
      } else {
        setError('Impossible de charger cet écran.');
      }
    } catch (e) {
      setError('Connexion impossible au serveur.');
    }
  }, [token]);

  useEffect(() => {
    fetchScreen();
    const id = setInterval(fetchScreen, REFRESH_MS);
    return () => clearInterval(id);
  }, [fetchScreen]);

  useEffect(() => {
    const updateScale = () => {
      if (!wrapperRef.current) return;
      const { clientWidth, clientHeight } = wrapperRef.current;
      setScale(Math.min(clientWidth / DESIGN_W, clientHeight / DESIGN_H));
    };
    updateScale();
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, []);

  if (error) {
    return (
      <div style={{ width: '100vw', height: '100vh', background: '#0b0f1c', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8b93ad', fontFamily: 'sans-serif', fontSize: 20 }}>
        {error}
      </div>
    );
  }

  return (
    <div ref={wrapperRef} style={{ width: '100vw', height: '100vh', background: '#0b0f1c', overflow: 'hidden' }}>
      <div
        style={{
          width: DESIGN_W,
          height: DESIGN_H,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          position: 'relative',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif',
        }}
      >
        {(screen?.blocks || []).map((block) => (
          <div
            key={block.id}
            style={{
              position: 'absolute',
              left: block.x,
              top: block.y,
              width: block.w,
              height: block.h,
              background: '#161e33',
              border: '1px solid #232c47',
              borderRadius: 20,
              overflow: 'hidden',
            }}
          >
            <BlockContent block={block} />
          </div>
        ))}
      </div>
    </div>
  );
}
