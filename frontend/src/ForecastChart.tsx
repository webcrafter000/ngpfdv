import React from 'react';
import {
  AreaChart,
  XAxis,
  YAxis,
  Tooltip,
  Area,
  ResponsiveContainer,
} from 'recharts';

type DataPoint = {
  start_time: string; // ISO string
  generation_mw: number;
  publish_time: string; // ISO string
};

type Props = {
  data: DataPoint[];
};

// Custom tooltip that shows forecast MW and publish timestamp
const CustomTooltip: React.FC<any> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const d = payload[0].payload;
    return (
      <div className="custom-tooltip" style={{ background: '#fff', border: '1px solid #ccc', padding: '5px' }}>
        <div>Forecast: {d.generation_mw} MW</div>
        <div>Published: {d.publish.toLocaleString()}</div>
      </div>
    );
  }
  return null;
};

export const ForecastChart: React.FC<Props> = ({ data }) => {
  // Convert ISO strings to Date objects for the X‑axis and tooltip
  const formatted = data.map((d) => ({
    ...d,
    start: new Date(d.start_time),
    publish: new Date(d.publish_time),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={formatted} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
        <XAxis
          dataKey="start"
          tickFormatter={(d) => new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        />
        <YAxis unit=" MW" />
        <Tooltip content={<CustomTooltip />} />
        <Area type="monotone" dataKey="generation_mw" stroke="#1976d2" fill="#90caf9" />
      </AreaChart>
    </ResponsiveContainer>
  );
};
