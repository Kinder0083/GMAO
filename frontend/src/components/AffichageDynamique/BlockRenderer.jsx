import React, { useEffect, useState } from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import {
  Activity, Gauge, Type, Image as ImageIcon, Clock, ListChecks, ClipboardList,
  BarChart3, QrCode, MonitorPlay, AlertTriangle,
} from 'lucide-react';
import './affichage-dynamique.css';

// Définition des types de blocs disponibles dans la palette de l'éditeur.
// `accent` sert à la fois à la puce de couleur affichée dans le bloc et au
// repère visuel dans la palette (cohérence de lecture à distance).
export const BLOCK_TYPES = [
  { type: 'cadence', label: 'Cadence équipement', icon: Gauge, accent: '#818cf8', defaultW: 480, defaultH: 280, defaultConfig: { machine_id: '' } },
  { type: 'mqtt_sensor', label: 'Capteur MQTT', icon: Activity, accent: '#60a5fa', defaultW: 360, defaultH: 220, defaultConfig: { sensor_id: '' } },
  { type: 'free_text', label: 'Texte libre', icon: Type, accent: '#94a3b8', defaultW: 480, defaultH: 160, defaultConfig: { text: 'Votre message ici' } },
  { type: 'image', label: 'Image / Logo', icon: ImageIcon, accent: '#c084fc', defaultW: 360, defaultH: 240, defaultConfig: { url: '' } },
  { type: 'clock', label: 'Horloge', icon: Clock, accent: '#fbbf24', defaultW: 320, defaultH: 200, defaultConfig: { label: '' } },
  { type: 'equipment_status', label: 'Statut équipements', icon: ListChecks, accent: '#34d399', defaultW: 400, defaultH: 320, defaultConfig: { equipment_ids: [] } },
  { type: 'work_orders', label: 'Ordres du jour', icon: ClipboardList, accent: '#fb923c', defaultW: 480, defaultH: 320, defaultConfig: { limit: 5, equipment_id: '' } },
  { type: 'kpi', label: 'Graphique / KPI', icon: BarChart3, accent: '#f472b6', defaultW: 340, defaultH: 280, defaultConfig: { machine_id: '', metric: 'trs' } },
  { type: 'qrcode', label: 'QR Code', icon: QrCode, accent: '#22d3ee', defaultW: 260, defaultH: 300, defaultConfig: { content: '', label: '' } },
  { type: 'ticker', label: 'Bandeau défilant', icon: MonitorPlay, accent: '#f87171', defaultW: 1000, defaultH: 90, defaultConfig: { text: 'Votre annonce ici', speed: 'normal' } },
];

export const KPI_METRICS = [
  { value: 'trs', label: 'TRS global (%)' },
  { value: 'cadence_per_min', label: 'Cadence (cp/min)' },
  { value: 'trs_availability', label: 'Disponibilité (%)' },
  { value: 'trs_performance', label: 'Performance (%)' },
  { value: 'trs_quality', label: 'Qualité (%)' },
  { value: 'rejects_today', label: 'Rebuts du jour' },
];

// Jetons de couleur par thème d'écran — réutilisés par l'éditeur et l'écran
// public pour que le fond/les cartes suivent le même thème que les blocs.
export const THEMES = {
  dark: {
    pageBg: '#0b0f1c',
    tileBg: '#161e33',
    tileBorder: '#232c47',
    textPrimary: '#ffffff',
    textMuted: '#8b93ad',
    trackBg: '#232c47',
  },
  light: {
    pageBg: '#eef1f6',
    tileBg: '#ffffff',
    tileBorder: '#dbe2ea',
    textPrimary: '#0f172a',
    textMuted: '#64748b',
    trackBg: '#e2e8f0',
  },
};

const STATUS_STYLES = {
  OPERATIONNEL: { label: 'En marche', color: '#4ade80' },
  EN_FONCTIONNEMENT: { label: 'En marche', color: '#4ade80' },
  A_LARRET: { label: 'À l\'arrêt', color: '#f87171' },
  EN_MAINTENANCE: { label: 'En maintenance', color: '#fbbf24' },
  HORS_SERVICE: { label: 'Hors service', color: '#f87171' },
  EN_CT: { label: 'En contrôle', color: '#60a5fa' },
  DEGRADE: { label: 'Dégradé', color: '#fbbf24' },
  ALERTE_S_EQUIP: { label: 'Alerte', color: '#f87171' },
};

const SPEED_DURATIONS = { lent: '35s', normal: '20s', rapide: '10s' };

// Un bloc "cadence" est en alerte si l'équipement est à l'arrêt ou que son TRS
// est sous l'objectif — utilisé par l'éditeur et l'écran public pour mettre en
// évidence la tuile elle-même (bordure pulsante), en plus du badge interne.
export function isBlockInAlert(block) {
  if (!block || block.type !== 'cadence') return false;
  const d = block.data || {};
  return d.is_running === false || (d.trs_target > 0 && d.trs < d.trs_target);
}

function useNow(intervalMs = 1000) {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}

function Sparkline({ history, color }) {
  if (!history || history.length < 2) return null;
  const chartData = history.map((d, i) => ({ i, v: Number(d.v) || 0 }));
  return (
    <div style={{ height: 36, marginTop: 10 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function AccentHeader({ icon: Icon, accent, children }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ width: 8, height: 8, borderRadius: 99, background: accent, flexShrink: 0 }} />
      {Icon && <Icon size={14} color={accent} style={{ flexShrink: 0 }} />}
      <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--ad-muted, #8b93ad)', textTransform: 'uppercase', letterSpacing: '.06em', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {children}
      </span>
    </div>
  );
}

// `theme` détermine les couleurs de texte/fond internes ; le fond/la bordure
// de la tuile elle-même sont posés par le composant parent (éditeur / écran
// public) à partir des mêmes jetons THEMES, pour rester cohérents.
export default function BlockContent({ block, theme = 'dark' }) {
  const { type, config = {}, data = {} } = block;
  const t = THEMES[theme] || THEMES.dark;
  const def = BLOCK_TYPES.find((b) => b.type === type);
  const accent = def?.accent || '#818cf8';
  const cssVars = { '--ad-muted': t.textMuted };

  switch (type) {
    case 'cadence': {
      const pct = data.theoretical ? Math.min(100, Math.round((data.cadence / data.theoretical) * 100)) : 0;
      const isAlert = data.is_running === false || (data.trs_target > 0 && data.trs < data.trs_target);
      return (
        <div style={{ ...cssVars, padding: 22, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
            <AccentHeader icon={def?.icon} accent={accent}>{data.machine_name || 'Cadence équipement'}</AccentHeader>
            {isAlert && (
              <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, fontWeight: 700, color: '#f87171', background: 'rgba(248,113,113,.15)', padding: '3px 8px', borderRadius: 99 }}>
                <AlertTriangle size={11} /> {data.is_running === false ? 'ARRÊT' : 'TRS BAS'}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 10 }}>
            <div style={{ fontSize: 58, fontWeight: 750, color: t.textPrimary, lineHeight: 1 }}>{data.cadence ?? '—'}</div>
            <div style={{ fontSize: 18, color: t.textMuted }}>cp/min</div>
          </div>
          <div style={{ marginTop: 14, height: 10, borderRadius: 6, background: t.trackBg, overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', background: isAlert ? '#f87171' : 'linear-gradient(90deg,#4f46e5,#818cf8)' }} />
          </div>
          {!!data.theoretical && (
            <div style={{ marginTop: 8, fontSize: 13, color: t.textMuted }}>Objectif : {data.theoretical} cp/min{data.trs_target ? ` · TRS objectif : ${data.trs_target}%` : ''}</div>
          )}
          <Sparkline history={data.history} color={accent} />
        </div>
      );
    }
    case 'mqtt_sensor': {
      return (
        <div style={{ ...cssVars, padding: 22, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <AccentHeader icon={def?.icon} accent={accent}>{data.nom || 'Capteur'}</AccentHeader>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginTop: 10 }}>
            <div style={{ fontSize: 48, fontWeight: 750, color: t.textPrimary, lineHeight: 1 }}>{data.value ?? '—'}</div>
            <div style={{ fontSize: 18, color: t.textMuted }}>{data.unit || ''}</div>
          </div>
          <Sparkline history={data.history} color={accent} />
        </div>
      );
    }
    case 'free_text': {
      return (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', padding: 24 }}>
          <div style={{ fontSize: 20, color: t.textPrimary, whiteSpace: 'pre-wrap' }}>{config.text}</div>
        </div>
      );
    }
    case 'image': {
      return (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 12 }}>
          {config.url ? (
            <img src={config.url} alt="" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
          ) : (
            <div style={{ color: t.textMuted, fontSize: 14 }}>Aucune image configurée</div>
          )}
        </div>
      );
    }
    case 'clock': {
      return <ClockBlock label={config.label} t={t} />;
    }
    case 'equipment_status': {
      const equipments = data.equipments || [];
      return (
        <div style={{ padding: 22, height: '100%', overflow: 'hidden' }}>
          <AccentHeader icon={def?.icon} accent={accent}>Statut équipements</AccentHeader>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 14 }}>
            {equipments.length === 0 && <div style={{ color: t.textMuted, fontSize: 14 }}>Aucun équipement</div>}
            {equipments.map((eq) => {
              const s = STATUS_STYLES[eq.statut] || { label: eq.statut, color: t.textMuted };
              return (
                <div key={eq.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 16, color: t.textPrimary }}>{eq.nom}</span>
                  <span style={{ fontSize: 12, fontWeight: 650, color: s.color, background: `${s.color}22`, padding: '4px 12px', borderRadius: 99 }}>{s.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      );
    }
    case 'work_orders': {
      const wos = data.work_orders || [];
      return (
        <div style={{ padding: 22, height: '100%', overflow: 'hidden' }}>
          <AccentHeader icon={def?.icon} accent={accent}>Ordres du jour</AccentHeader>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 15, color: t.textPrimary, marginTop: 14 }}>
            {wos.length === 0 && <div style={{ color: t.textMuted, fontSize: 14 }}>Aucun ordre en cours</div>}
            {wos.map((wo, i) => (
              <div key={i}>#{wo.numero} — {wo.titre}</div>
            ))}
          </div>
        </div>
      );
    }
    case 'kpi': {
      const metricDef = KPI_METRICS.find((m) => m.value === config.metric);
      return (
        <div style={{ padding: 22, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <AccentHeader icon={def?.icon} accent={accent}>{metricDef?.label || 'KPI'}</AccentHeader>
          <div style={{ fontSize: 44, fontWeight: 750, color: t.textPrimary, marginTop: 8 }}>{data.value ?? '—'}</div>
          <Sparkline history={data.history} color={accent} />
        </div>
      );
    }
    case 'qrcode': {
      return (
        <div style={{ padding: 20, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
          {data.qr_data_uri ? (
            <img src={data.qr_data_uri} alt="QR code" style={{ maxWidth: '80%', maxHeight: '70%', background: '#fff', padding: 8, borderRadius: 8 }} />
          ) : (
            <div style={{ color: t.textMuted, fontSize: 14 }}>Aucun contenu configuré</div>
          )}
          {config.label && <div style={{ fontSize: 14, color: t.textPrimary, textAlign: 'center' }}>{config.label}</div>}
        </div>
      );
    }
    case 'ticker': {
      const duration = SPEED_DURATIONS[config.speed] || SPEED_DURATIONS.normal;
      return (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', overflow: 'hidden', padding: '0 20px', background: 'rgba(248,113,113,.08)' }}>
          <span className="ad-ticker-track" style={{ animationDuration: duration, fontSize: 22, fontWeight: 600, color: t.textPrimary }}>
            {config.text || 'Votre annonce ici'}
          </span>
        </div>
      );
    }
    default:
      return <div style={{ padding: 16, color: t.textMuted }}>Bloc inconnu</div>;
  }
}

function ClockBlock({ label, t }) {
  const now = useNow(1000);
  const time = now.toLocaleTimeString('fr-FR');
  const date = now.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  return (
    <div style={{ padding: 22, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      {label && <div style={{ fontSize: 13, fontWeight: 600, color: t.textMuted, textTransform: 'uppercase', letterSpacing: '.06em' }}>{label}</div>}
      <div style={{ fontSize: 44, fontWeight: 700, color: t.textPrimary, lineHeight: 1, marginTop: label ? 8 : 0 }}>{time}</div>
      <div style={{ fontSize: 14, color: t.textMuted, marginTop: 6, textTransform: 'capitalize' }}>{date}</div>
    </div>
  );
}
