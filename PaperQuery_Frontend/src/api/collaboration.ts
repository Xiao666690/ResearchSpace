import api from '@/api/api'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export interface ProjectMember { username: string; role: 'OWNER' | 'EDITOR' | 'VIEWER'; joined_at?: string }
export interface ProjectComment { comment_id: string; username: string; target_type: string; target_id: string; content: string; created_at?: string }
export interface Assignment { task_id: string; goal: string; username: string; assigned_at?: string }
const base = (id: string) => `/projects/${id}/collaboration`
export const listMembers = async (id: string): Promise<ProjectMember[]> => (await api.get(`${base(id)}/members`, auth())).data.data
export const addMember = async (id: string, username: string, role: ProjectMember['role']) =>
  api.post(`${base(id)}/members`, { username, role }, auth())
export const removeMember = async (id: string, username: string) => api.delete(`${base(id)}/members/${username}`, auth())
export const listComments = async (id: string): Promise<ProjectComment[]> => (await api.get(`${base(id)}/comments`, auth())).data.data
export const addComment = async (id: string, targetType: string, targetId: string, content: string) =>
  api.post(`${base(id)}/comments`, { target_type: targetType, target_id: targetId, content }, auth())
export const listAssignments = async (id: string): Promise<Assignment[]> => (await api.get(`${base(id)}/assignments`, auth())).data.data
export const assignTask = async (id: string, taskId: string, username: string) =>
  api.post(`${base(id)}/assignments`, { task_id: taskId, username }, auth())
