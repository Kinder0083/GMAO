import React, { useEffect, useState } from 'react';
import { Activity, Gauge, Type, Image as ImageIcon, Clock, ListChecks, ClipboardList, BarChart3 } from 'lucide-react';

// Définition des types de blocs disponibles dans la palette de l'éditeur.
export const BLOCK_TYPES = [
  { type: 'cadence', label: 'Cadence équipement', icon: Gauge, defaultW: 480, defaultH: 260, defaultConfig: { machine_id: '' } },
  { type: 'mqtt_sensor', label: 'Capteur MQTT', icon: Activity, defaultW: 360, defaultH: 200, defaultConfig: { sensor_id: '' } },
  { type: 'free_text', label: 'Texte libre', icon: Type, defaultW: 480, defaultH: 160, defaultConfig: { text: 'Votre message ici' } },
  { type: 'image', label: 'Image / Logo', icon: ImageIcon, defaultW: 360, defaultH: 240, defaultConfig: { url: '' } },
  { type: 'clock', label: 'Horloge', icon: Clock, defaultW: 320, defaultH: 200, defaultConfig: { label: '' } },
  { type: 'equipment_status', label: 'Statut équipements', icon: ListChecks, defaultW: 400, defaultH: 320, defaultConfig: { equipment_ids: [] } },
  { type: 'work_orders', label: 'Ordres du jour', icon: ClipboardList, defaultW: 480, defaultH: 320, defaultConfig: { limit: 5, equipment_id: '' } },
  { type: 'kpi', label: 'Graphique / KPI', icon: BarChart3, defaultW: 320, defaultH: 260, defaultConfig: { machine_id: '', metric: 'trs' } },
];

export const KPI_METRICS = [
  { value: 'trs', label: 'TRS global (%)' },
  { value: 'cadence_per_min', label: 'Cadence (cp/min)' },
  { value: 'trs_availability', label: 'Disponibilité (%)' },
  { value: 'trs_performance', label: 'Performance (%)' },
  { value: 'trs_quality', label: 'Qualité (%)' },
  { value: 'rejects_today', label: 'Rebuts du jour' },
];

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

function useNow(intervalMs = 1000) {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}

const lbl = { fontSize: 13, fontWeight: 600, color: '#8b93ad', textTransform: 'uppercase', letterSpacing: '.06em' };

export default function BlockContent({ block }) {
  const { type, config = {}, data = {} } = block;

  switch (type) {
    case 'cadence': {
      const pct = data.theoretical ? Math.min(100, Math.round((data.cadence / data.theoretical) * 100)) : 0;
      return (
        <div style={{ padding: 24, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={lbl}>{data.machine_name || 'Cadence équipement'}</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginTop: 10 }}>
            <div style={{ fontSize: 64, fontWeight: 750, color: '#fff', lineHeight: 1 }}>{data.cadence ?? '—'}</div>
            <div style={{ fontSize: 18, color: '#8b93ad' }}>cp/min</div>
          </div>
          <div style={{ marginTop: 14, height: 10, borderRadius: 6, background: '#232c47', overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', background: 'linear-gradient(90deg,#4f46e5,#818cf8)' }} />
          </div>
          {!!data.theoretical && (
            <div style={{ marginTop: 8, fontSize: 13, color: '#8b93ad' }}>Objectif : {data.theoretical} cp/min</div>
          )}
        </div>
      );
    }
    case 'mqtt_sensor': {
      return (
        <div style={{ padding: 24, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <div style={lbl}>{data.nom || 'Capteur'}</div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginTop: 10 }}>
            <div style={{ fontSize: 52, fontWeight: 750, color: '#fff', lineHeight: 1 }}>{data.value ?? '—'}</div>
            <div style={{ fontSize: 18, color: '#8b93ad' }}>{data.unit || ''}</div>
          </div>
        </div>
      );
    }
    case 'free_text': {
      return (
        <div style={{ padding: 24, height: '100%', display: 'flex', alignItems: 'center' }}>
          <div style={{ fontSize: 20, color: '#e5e7eb', whiteSpace: 'pre-wrap' }}>{config.text}</div>
        </div>
      );
    }
    case 'image': {
      return (
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 12 }}>
          {config.url ? (
            <img src={config.url} alt="" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
          ) : (
            <div style={{ color: '#8b93ad', fontSize: 14 }}>Aucune image configurée</div>
          )}
        </div>
      );
    }
    case 'clock': {
      return <ClockBlock label={config.label} />;
    }
    case 'equipment_status': {
      const equipments = data.equipments || [];
      return (
        <div style={{ padding: 22, height: '100%', overflow: 'hidden' }}>
          <div style={{ ...lbl, marginBottom: 14 }}>Statut équipements</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {equipments.length === 0 && <div style={{ color: '#8b93ad', fontSize: 14 }}>Aucun équipement</div>}
            {equipments.map((eq) => {
              const s = STATUS_STYLES[eq.statut] || { label: eq.statut, color: '#8b93ad' };
              return (
                <div key={eq.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 16, color: '#e5e7eb' }}>{eq.nom}</span>
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
          <div style={{ ...lbl, marginBottom: 14 }}>Ordres du jour</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 15, color: '#e5e7eb' }}>
            {wos.length === 0 && <div style={{ color: '#8b93ad', fontSize: 14 }}>Aucun ordre en cours</div>}
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
          <div style={lbl}>{metricDef?.label || 'KPI'}</div>
          <div style={{ fontSize: 48, fontWeight: 750, color: '#fff', marginTop: 8 }}>{data.value ?? '—'}</div>
        </div>
      );
    }
    default:
      return <div style={{ padding: 16, color: '#8b93ad' }}>Bloc inconnu</div>;
  }
}

function ClockBlock({ label }) {
  const now = useNow(1000);
  const time = now.toLocaleTimeString('fr-FR');
  const date = now.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  return (
    <div style={{ padding: 22, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      {label && <div style={lbl}>{label}</div>}
      <div style={{ fontSize: 44, fontWeight: 700, color: '#fff', lineHeight: 1, marginTop: label ? 8 : 0 }}>{time}</div>
      <div style={{ fontSize: 14, color: '#8b93ad', marginTop: 6, textTransform: 'capitalize' }}>{date}</div>
    </div>
  );
}
