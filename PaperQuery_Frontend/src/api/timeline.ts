import api from '@/api/api'
const auth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
export interface TimelineEvent {
  id: number
  event_type: string
  target_type?: string
  target_id?: string
  title?: string
  description?: string
  created_at?: string
  metadata?: Record<string, any>
}
export const listTimeline = async (projectId: string): Promise<TimelineEvent[]> =>
  (await api.get(`/projects/${projectId}/timeline`, auth())).data.data
