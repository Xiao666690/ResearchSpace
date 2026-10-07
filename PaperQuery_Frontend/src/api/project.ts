import api from '@/api/api'

export interface ResearchProject {
  project_id: string
  name: string
  description: string
  research_goal: string
  status: 'active' | 'archived'
  created_by: string
  created_at?: string
}

export interface ProjectPaper {
  knowledge_id: string
  document_id: string
  document_name: string
  document_status: number
  added_by?: string
}

const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export const listProjects = async (includeArchived = false): Promise<ResearchProject[]> =>
  (await api.get('/projects', { ...auth(), params: { include_archived: includeArchived } })).data.data
export const getProject = async (id: string): Promise<ResearchProject> =>
  (await api.get(`/projects/${id}`, auth())).data.data
export const createProject = async (name: string, description = '', researchGoal = ''): Promise<ResearchProject> =>
  (await api.post('/projects', { name, description, research_goal: researchGoal }, auth())).data.data
export const updateProject = async (id: string, values: Partial<Pick<ResearchProject, 'name' | 'description' | 'research_goal'>>): Promise<ResearchProject> =>
  (await api.put(`/projects/${id}`, values, auth())).data.data
export const archiveProject = async (id: string) => api.delete(`/projects/${id}`, auth())
export const restoreProject = async (id: string) => api.post(`/projects/${id}/restore`, {}, auth())
export const projectOverview = async (id: string) => (await api.get(`/projects/${id}/overview`, auth())).data.data
export const listProjectDocuments = async (id: string): Promise<ProjectPaper[]> =>
  (await api.get(`/projects/${id}/documents`, auth())).data.data
export const addProjectDocument = async (id: string, knowledgeId: string, documentId: string) =>
  api.post(`/projects/${id}/documents`, { knowledge_id: knowledgeId, document_id: documentId }, auth())
export const removeProjectDocument = async (id: string, knowledgeId: string, documentId: string) =>
  api.delete(`/projects/${id}/documents/${documentId}`, { ...auth(), params: { knowledge_id: knowledgeId } })
