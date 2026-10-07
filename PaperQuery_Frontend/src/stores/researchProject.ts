import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProject, listProjectDocuments, type ProjectPaper, type ResearchProject } from '@/api/project'

export const useResearchProjectStore = defineStore('researchProject', () => {
  const currentProjectId = ref<string | null>(localStorage.getItem('researchProjectId'))
  const currentProject = ref<ResearchProject | null>(null)
  const projectDocuments = ref<ProjectPaper[]>([])

  function setCurrentProject(id: string | null) {
    currentProjectId.value = id
    if (id) localStorage.setItem('researchProjectId', id)
    else localStorage.removeItem('researchProjectId')
  }
  async function loadCurrentProject(id = currentProjectId.value) {
    if (!id) return clearCurrentProject()
    try {
      const project = await getProject(id)
      if (project.status !== 'active') return clearCurrentProject()
      currentProject.value = project
      setCurrentProject(id)
      await loadProjectDocuments()
    } catch (error) {
      clearCurrentProject()
      throw error
    }
  }
  async function loadProjectDocuments() {
    projectDocuments.value = currentProjectId.value ? await listProjectDocuments(currentProjectId.value) : []
  }
  function clearCurrentProject() {
    setCurrentProject(null)
    currentProject.value = null
    projectDocuments.value = []
  }
  return { currentProjectId, currentProject, projectDocuments, setCurrentProject,
    loadCurrentProject, loadProjectDocuments, clearCurrentProject }
})
