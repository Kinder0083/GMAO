import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { BACKEND_URL } from '../utils/config';
import BlockContent, { THEMES, isBlockInAlert } from '../components/AffichageDynamique/BlockRenderer';

const API = BACKEND_URL;
const DESIGN_W = 1920;
const DESIGN_H = 1080;
const REFRESH_MS = 30000;
const HEADER_H = 84;

function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

// Page publique, sans authentification : lecture seule (aucun appel d'écriture ici).
// Destinée aux lecteurs de signalétique (Yodeck, OptiSigns, navigateur en kiosque, etc.)
//
// Rotation multi-écrans : ajouter ?rotate=jeton2,jeton3&interval=20 à l'URL
// pour faire défiler plusieurs écrans sur un même afficheur physique (le jeton
// de la route est inclus en premier). Sans ce paramètre, comportement inchangé
// (un seul écran fixe).
export default function AffichageDynamiquePublicPage() {
  const { token } = useParams();
  const [searchParams] = useSearchParams();

  const tokenSequence = useMemo(() => {
    const rotateParam = searchParams.get('rotate');
    if (!rotateParam) return [token];
    const extra = rotateParam.split(',').map((t) => t.trim()).filter(Boolean);
    return [token, ...extra];
  }, [token, searchParams]);
  const rotateInterval = Math.max(5, parseInt(searchParams.get('interval'), 10) || 20) * 1000;

  const [activeIndex, setActiveIndex] = useState(0);
  const activeToken = tokenSequence[activeIndex % tokenSequence.length];

  const [screen, setScreen] = useState(null);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [scale, setScale] = useState(1);
  const wrapperRef = useRef(null);
  const clock = useClock();

  // Rotation entre écrans (si plusieurs jetons)
  useEffect(() => {
    if (tokenSequence.length <= 1) return;
    const id = setInterval(() => setActiveIndex((i) => (i + 1) % tokenSequence.length), rotateInterval);
    return () => clearInterval(id);
  }, [tokenSequence.length, rotateInterval]);

  const fetchScreen = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/affichage-dynamique/public/${activeToken}`);
      if (res.ok) {
        const d = await res.json();
        setScreen(d);
        setError(null);
        setLastRefresh(new Date());
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
  }, [activeToken]);

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
  }, [screen?.header?.enabled]);

  const theme = THEMES[screen?.theme] || THEMES.dark;
  const header = screen?.header;

  if (error) {
    return (
      <div style={{ width: '100vw', height: '100vh', background: theme.pageBg, display: 'flex', alignItems: 'center', justifyContent: 'center', color: theme.textMuted, fontFamily: 'sans-serif', fontSize: 20 }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ width: '100vw', height: '100vh', background: theme.pageBg, display: 'flex', flexDirection: 'column', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif' }}>
      {header?.enabled && (
        <div style={{ height: HEADER_H, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 32px', borderBottom: `1px solid ${theme.tileBorder}` }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {header.logo_url && <img src={header.logo_url} alt="" style={{ height: 44, maxWidth: 160, objectFit: 'contain' }} />}
            <div style={{ fontSize: 24, fontWeight: 700, color: theme.textPrimary }}>{header.title || ''}</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <LiveDot lastRefresh={lastRefresh} textColor={theme.textMuted} />
            <div style={{ fontSize: 22, fontWeight: 600, color: theme.textPrimary, fontVariantNumeric: 'tabular-nums' }}>
              {clock.toLocaleTimeString('fr-FR')}
            </div>
          </div>
        </div>
      )}
      <div ref={wrapperRef} style={{ flex: 1, minHeight: 0, overflow: 'hidden', position: 'relative' }}>
        {!header?.enabled && (
          <div style={{ position: 'absolute', top: 14, right: 18, zIndex: 5 }}>
            <LiveDot lastRefresh={lastRefresh} textColor={theme.textMuted} />
          </div>
        )}
        <div
          style={{
            width: DESIGN_W,
            height: DESIGN_H,
            transform: `scale(${scale})`,
            transformOrigin: 'top left',
            position: 'relative',
          }}
        >
          {(screen?.blocks || []).map((block) => (
            <div
              key={block.id}
              className={isBlockInAlert(block) ? 'ad-alert-border' : ''}
              style={{
                position: 'absolute',
                left: block.x,
                top: block.y,
                width: block.w,
                height: block.h,
                background: theme.tileBg,
                border: `1px solid ${theme.tileBorder}`,
                borderRadius: 20,
                overflow: 'hidden',
              }}
            >
              <BlockContent block={block} theme={screen?.theme || 'dark'} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function LiveDot({ lastRefresh, textColor }) {
  const label = lastRefresh ? lastRefresh.toLocaleTimeString('fr-FR') : '…';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: textColor }}>
      <span className="ad-live-dot" style={{ width: 8, height: 8, borderRadius: 99, background: '#4ade80', display: 'inline-block' }} />
      Mise à jour {label}
    </div>
  );
}
