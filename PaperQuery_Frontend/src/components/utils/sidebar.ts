import { LayoutDashboard, LibraryBig, MessagesSquare, FlaskConical, UsersRound,
  FolderKanban, Network, BookMarked, Table2, Clock3, PenLine, NotebookPen } from 'lucide-vue-next'

export interface SidebarItem { title: string; icon: any; link: string }
export interface SidebarGroup { title: string; items: SidebarItem[] }

export const getSidebarGroups = (role?: string | null, projectId?: string | null): SidebarGroup[] => {
  const project = projectId ? `/home/projects/${projectId}` : ''
  const groups: SidebarGroup[] = [
    { title: 'HOME', items: [
      { title: '概览', icon: LayoutDashboard, link: '/home/dashboard' },
      { title: '研究项目', icon: FolderKanban, link: '/home/projects' },
    ] },
    { title: 'EXPLORE', items: [
      { title: '论文资料', icon: LibraryBig, link: project ? `${project}/library` : '/home/library' },
      ...(project ? [{ title: 'Research Map', icon: Network, link: `${project}/map` }] : []),
    ] },
    { title: 'THINK', items: [
      ...(project ? [{ title: 'Evidence Board', icon: BookMarked, link: `${project}/evidence` },
        { title: 'Compare Lab', icon: Table2, link: `${project}/compare` }] : []),
      { title: '科研笔记', icon: NotebookPen, link: '/home/library/notes' },
    ] },
    { title: 'RESEARCH', items: [
      { title: '智能问答', icon: MessagesSquare, link: project ? `${project}/chat` : '/home/chat' },
      { title: 'Research Missions', icon: FlaskConical, link: project ? `${project}/research` : '/home/research' },
      ...(project ? [{ title: 'Research Timeline', icon: Clock3, link: `${project}/timeline` }] : []),
    ] },
  ]
  if (project) groups.push({ title: 'CREATE', items: [
    { title: 'Research Studio', icon: PenLine, link: `${project}/studio` },
  ] })
  const collaborate: SidebarItem[] = []
  if (project) collaborate.push({ title: '协作空间', icon: UsersRound, link: `${project}/collaboration` })
  if (role === 'admin') collaborate.push({ title: '管理团队', icon: UsersRound, link: '/home/team' })
  if (collaborate.length) groups.push({ title: 'COLLABORATE', items: collaborate })
  return groups
}
