import api from '@/api/api'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export interface StudioDocument {
  studio_id: string
  title: string
  document_type: string
  content_markdown: string
  created_by?: string
  updated_at?: string
  citations: Array<{ citation_key: string; knowledge_id: string; document_id: string; page: number; chunk_id: string; source_status: string }>
}
export const listStudio = async (id: string): Promise<StudioDocument[]> =>
  (await api.get(`/projects/${id}/studio`, auth())).data.data
export const createStudio = async (id: string, title: string): Promise<StudioDocument> =>
  (await api.post(`/projects/${id}/studio`, { title }, auth())).data.data
export const updateStudio = async (id: string, studioId: string, title: string, content: string): Promise<StudioDocument> =>
  (await api.put(`/projects/${id}/studio/${studioId}`, { title, content_markdown: content }, auth())).data.data
export const importArtifact = async (id: string, artifactId: string): Promise<StudioDocument> =>
  (await api.post(`/projects/${id}/studio/import-artifact`, { artifact_id: artifactId }, auth())).data.data
export const addStudioCitation = async (id: string, studioId: string, value: { citation_key: string; knowledge_id: string; document_id: string; page_number: number; chunk_id: string }): Promise<StudioDocument> =>
  (await api.post(`/projects/${id}/studio/${studioId}/citations`, value, auth())).data.data
