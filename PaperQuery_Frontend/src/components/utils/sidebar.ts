import { LayoutDashboard, LibraryBig, MessagesSquare, FlaskConical, UsersRound,
  FolderKanban, Network, BookMarked, Table2, Clock3, PenLine, NotebookPen } from 'lucide-vue-next'

export interface SidebarItem { title: string; icon: any; link: string }
export interface SidebarGroup { title: string; items: SidebarItem[] }

export const getSidebarGroups = (role?: string | null, projectId?: string | null): SidebarGroup[] => {
  const project = projectId ? `/home/projects/${projectId}` : ''
  const groups: SidebarGroup[] = [
    { title: '工作空间', items: [
      { title: '概览', icon: LayoutDashboard, link: '/home/dashboard' },
      { title: '研究项目', icon: FolderKanban, link: '/home/projects' },
    ] },
    { title: '探索资料', items: [
      { title: '论文资料', icon: LibraryBig, link: project ? `${project}/library` : '/home/library' },
      ...(project ? [{ title: '研究图谱', icon: Network, link: `${project}/map` }] : []),
    ] },
    { title: '整理思考', items: [
      ...(project ? [{ title: '证据看板', icon: BookMarked, link: `${project}/evidence` },
        { title: '方法比较', icon: Table2, link: `${project}/compare` }] : []),
      { title: '科研笔记', icon: NotebookPen, link: '/home/library/notes' },
    ] },
    { title: '研究行动', items: [
      { title: '智能问答', icon: MessagesSquare, link: project ? `${project}/chat` : '/home/chat' },
      { title: '研究任务', icon: FlaskConical, link: project ? `${project}/research` : '/home/research' },
      ...(project ? [{ title: '研究时间线', icon: Clock3, link: `${project}/timeline` }] : []),
    ] },
  ]
  if (project) groups.push({ title: '成果创作', items: [
    { title: '成果工作室', icon: PenLine, link: `${project}/studio` },
  ] })
  const collaborate: SidebarItem[] = []
  if (project) collaborate.push({ title: '协作空间', icon: UsersRound, link: `${project}/collaboration` })
  if (role === 'admin') collaborate.push({ title: '管理团队', icon: UsersRound, link: '/home/team' })
  if (collaborate.length) groups.push({ title: '团队协作', items: collaborate })
  return groups
}
