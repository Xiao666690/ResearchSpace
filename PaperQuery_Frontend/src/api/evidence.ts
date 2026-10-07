import api from '@/api/api'
import type { CitationItem } from '@/api/qa'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export interface SavedEvidence {
  evidence_id: string
  knowledge_id: string
  document_id: string
  page_number: number
  chunk_id: string
  text: string
  stance: string
  source_status: 'available' | 'deleted'
}
export interface Claim {
  claim_id: string
  title: string
  content: string
  status: string
  evidence: SavedEvidence[]
}
export const listClaims = async (id: string): Promise<Claim[]> =>
  (await api.get(`/projects/${id}/evidence`, auth())).data.data
export const createClaim = async (id: string, title: string, content: string): Promise<Claim> =>
  (await api.post(`/projects/${id}/evidence`, { title, content }, auth())).data.data
export const addClaimCitation = async (id: string, claimId: string, citation: CitationItem, stance = 'SUPPORT') =>
  api.post(`/projects/${id}/evidence/${claimId}/citations`, {
    knowledge_id: citation.knowledgeID, document_id: citation.documentID,
    page_number: citation.page, chunk_id: citation.chunk_id, stance,
  }, auth())
export const deleteClaim = async (id: string, claimId: string) =>
  api.delete(`/projects/${id}/evidence/${claimId}`, auth())
