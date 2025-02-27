import { create } from 'zustand';

const useDiaryStore = create((set) => ({
  diaryEntries: [],
  summary: null,
  loading: false,
  error: null,

  setDiaryEntries: (entries) => set({ diaryEntries: entries }),

  setSummary: (summary) => set({ summary }),

  setLoading: (isLoading) => set({ loading: isLoading }),

  setError: (error) => set({ error }),
}));

export default useDiaryStore;
