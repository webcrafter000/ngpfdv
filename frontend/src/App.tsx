import React, { useState } from 'react';
import { ForecastView } from './screens/ForecastView';
import { AccuracyView } from './screens/AccuracyView';
import './App.css';

// Hard‑coded default for the demo; 2026‑01‑15 contains seeded data.
const defaultDate = '2026-01-15';

export const App: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(defaultDate);
  const [tab, setTab] = useState<'forecast' | 'accuracy'>('forecast');

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(e.target.value);
  };

  return (
    <div className="app">
      <header>
        <h1>Wind Forecast Decision Support Portal</h1>
        <div className="controls">
          <label>
            Delivery Day:
            <input
              type="date"
              value={selectedDate}
              min="2026-01-01"
              max="2026-01-31"
              onChange={handleDateChange}
            />
          </label>
          <nav>
            <button
              className={tab === 'forecast' ? 'active' : ''}
              onClick={() => setTab('forecast')}
            >
              Forecast
            </button>
            <button
              className={tab === 'accuracy' ? 'active' : ''}
              onClick={() => setTab('accuracy')}
            >
              Accuracy
            </button>
          </nav>
        </div>
      </header>

      <main>{tab === 'forecast' ? <ForecastView date={selectedDate} /> : <AccuracyView date={selectedDate} />}</main>
    </div>
  );
};

export default App;
