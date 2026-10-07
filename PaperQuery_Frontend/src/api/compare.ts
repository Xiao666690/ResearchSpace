import api from '@/api/api'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }, timeout: 120000 })
export interface ComparisonCell {
  value: string
  verified: boolean
  citation: { document_id: string; knowledge_id: string; page: number; chunk_id: string } | null
  source_status: string
}
export interface Comparison {
  session_id: string
  title: string
  question: string
  columns: string[]
  rows: Array<{ document_id: string; paper: string; cells: Record<string, ComparisonCell> }>
  created_at?: string
}
export const listComparisons = async (id: string): Promise<Comparison[]> =>
  (await api.get(`/projects/${id}/compare`, auth())).data.data
export const createComparison = async (id: string, question: string, documentIds: string[], columns: string[]): Promise<Comparison> =>
  (await api.post(`/projects/${id}/compare`, { question, document_ids: documentIds, columns }, auth())).data.data
