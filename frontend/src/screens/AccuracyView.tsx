import React, { useEffect, useState } from 'react';
import { fetchErrorSummary } from '../api';
import { ErrorChart } from '../ErrorChart';
import { KpiStrip } from '../KpiStrip';

type Row = {
  start_time: string;
  forecast_mw: number;
  actual_mw: number;
  error_mw: number;
};

type Aggregates = {
  mae: number;
  bias: number;
  max_abs_error: number;
  by_hour: { hour: number; mae: number; bias: number }[];
};

export const AccuracyView: React.FC<{ date: string }> = ({ date }) => {
  const [rows, setRows] = useState<Row[]>([]);
  const [aggs, setAggs] = useState<Aggregates | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchErrorSummary(date)
      .then((res) => {
        setRows(res.rows);
        setAggs(res.aggregates);
      })
      .finally(() => setLoading(false));
  }, [date]);

  return (
    <div>
      <h2>Accuracy for {date}</h2>
      {loading ? (
        <p>Loading…</p>
      ) : rows.length === 0 ? (
        <p>No data for {date}. Has the January 2026 ingest been run?</p>
      ) : (
        aggs && (
          <>
            <KpiStrip
              items={[
                { label: 'MAE', value: `${aggs.mae.toFixed(2)} MW` },
                { label: 'Bias', value: `${aggs.bias.toFixed(2)} MW` },
                { label: 'Max |Error|', value: `${aggs.max_abs_error.toFixed(2)} MW` },
              ]}
            />
            <ErrorChart rows={rows} hourly={aggs.by_hour} />
          </>
        )
      )}
    </div>
  );
};
