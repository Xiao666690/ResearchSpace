import api from '@/api/api'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export interface GraphSource { knowledge_id: string; document_id: string; page: number; chunk_id: string }
export interface GraphNode { id: string; type: string; name: string; confidence: string; citation: GraphSource; source_status: string }
export interface GraphEdge { id: string; source: string; target: string; type: string; confidence: string; citation: GraphSource; source_status: string }
export interface ResearchGraph { run: { run_id: string; status: string; error?: string } | null; nodes: GraphNode[]; edges: GraphEdge[] }
export const getGraph = async (id: string): Promise<ResearchGraph> =>
  (await api.get(`/projects/${id}/graph`, auth())).data.data
export const buildGraph = async (id: string) =>
  (await api.post(`/projects/${id}/graph/build`, {}, auth())).data.data
