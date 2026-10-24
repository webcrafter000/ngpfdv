import React, { useEffect, useState } from 'react';
import { fetchForecast } from '../api';
import { ForecastChart } from '../ForecastChart';
import { KpiStrip } from '../KpiStrip';

type ForecastItem = {
  start_time: string;   // ISO
  publish_time: string; // ISO
  generation_mw: number;
};

export const ForecastView: React.FC<{ date: string }> = ({ date }) => {
  const [data, setData] = useState<ForecastItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchForecast(date).then(setData).finally(() => setLoading(false));
  }, [date]);

  // Compute KPIs
  const peak = data.reduce((max, d) => (d.generation_mw > max ? d.generation_mw : max), 0);
  const avg = data.reduce((sum, d) => sum + d.generation_mw, 0) / (data.length || 1);
  const count = data.length;

  return (
    <div>
      <h2>Forecast for {date}</h2>
      {loading ? (
        <p>Loading…</p>
      ) : data.length === 0 ? (
        <p>No data for {date}. Has the January 2026 ingest been run?</p>
      ) : (
        <>
          <KpiStrip
            items={[
              { label: 'Peak', value: `${peak.toFixed(1)} MW` },
              { label: 'Average', value: `${avg.toFixed(1)} MW` },
              { label: 'Periods', value: count },
            ]}
          />
          <ForecastChart data={data} />
          <p style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>
            Hover over the area to see when each forecast was published.
          </p>
        </>
      )}
    </div>
  );
};
