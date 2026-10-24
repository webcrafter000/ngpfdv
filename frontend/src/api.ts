import axios from 'axios';

// Base URL is injected at build time via Vite env variables.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export const fetchForecast = async (date: string) => {
  const response = await axios.get(`${API_BASE_URL}/api/forecast`, {
    params: { date },
  });
  return response.data; // [{start_time:string,publish_time:string,generation_mw:number},...]
};

export const fetchActuals = async (date: string) => {
  const response = await axios.get(`${API_BASE_URL}/api/actuals`, {
    params: { date },
  });
  return response.data; // [{start_time:string,generation_mw:number},...]
};

export const fetchErrorSummary = async (date: string) => {
  const response = await axios.get(`${API_BASE_URL}/api/error-summary`, {
    params: { date },
  });
  return response.data; // {rows:..., aggregates:...}
};
