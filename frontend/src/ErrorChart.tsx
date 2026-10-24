import React from 'react';
import {
  ComposedChart,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  Line,
  BarChart,
  ResponsiveContainer,
} from 'recharts';

type Row = {
  start_time: string; // ISO
  forecast_mw: number;
  actual_mw: number;
  error_mw: number;
};

type HourAgg = {
  hour: number;
  mae: number;
  bias: number; // added bias to match API contract
};

type Props = {
  rows: Row[];
  hourly: HourAgg[];
};

export const ErrorChart: React.FC<Props> = ({ rows, hourly }) => {
  const formattedRows = rows.map((r) => ({
    ...r,
    start: new Date(r.start_time),
  }));

  return (
    <>
      {/* Main chart – forecast vs actual with error line */}
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={formattedRows} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <XAxis
            dataKey="start"
            tickFormatter={(d) => new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          />
          <YAxis unit=" MW" />
          <Tooltip
            labelFormatter={(label) => `Start: ${new Date(label).toLocaleString()}`}
            formatter={(value, name) => [`${value} MW`, name.replace('_', ' ') ]}
          />
          <Legend />
          <Line type="monotone" dataKey="forecast_mw" name="Forecast" stroke="#1976d2" />
          <Line type="monotone" dataKey="actual_mw" name="Actual" stroke="#ff9800" />
          <Bar dataKey="error_mw" name="Error" fill="#e53935" />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Small bar chart – MAE by hour */}
      <h3 style={{ marginTop: '1rem' }}>Mean Absolute Error by Hour</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={hourly}>
          <XAxis dataKey="hour" label={{ value: 'Hour (UTC)', position: 'insideBottom' }} />
          <YAxis unit=" MW" />
          <Tooltip />
          <Bar dataKey="mae" fill="#4caf50" name="MAE" />
        </BarChart>
      </ResponsiveContainer>
    </>
  );
};
