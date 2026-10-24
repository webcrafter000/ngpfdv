import React from 'react';
import './KpiStrip.css';

type Props = {
  items: { label: string; value: string | number }[];
};

export const KpiStrip: React.FC<Props> = ({ items }) => (
  <div className="kpi-strip">
    {items.map((item, i) => (
      <div key={i} className="kpi-item">
        <div className="kpi-label">{item.label}</div>
        <div className="kpi-value">{item.value}</div>
      </div>
    ))}
  </div>
);
