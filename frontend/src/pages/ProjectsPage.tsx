import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, FolderOpen, ArrowRight } from 'lucide-react'
import api from '../services/api'

interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
}

const ProjectsPage = () => {
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '' })
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const { data: projects = [], isLoading } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await api.get('/projects')
      return response.data
    }
  })

  const createMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      return await api.post('/projects', data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowModal(false)
      setFormData({ name: '', description: '' })
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      return await api.delete(`/projects/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Projects</h1>
          <p className="text-slate-500 text-sm mt-0.5">Organize your datasets into projects</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors shadow-sm"
        >
          <Plus size={16} />
          New Project
        </button>
      </div>

      {/* Projects grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-40 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-slate-200 shadow-card">
          <div className="w-16 h-16 rounded-xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
            <FolderOpen size={28} className="text-indigo-400" />
          </div>
          <p className="text-slate-600 font-medium mb-1">No projects yet</p>
          <p className="text-slate-400 text-sm mb-4">Create your first project to get started</p>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors"
          >
            <Plus size={16} />
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white rounded-xl border border-slate-200 shadow-card p-6 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
                  <FolderOpen size={18} className="text-indigo-500" />
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    if (confirm(`Delete project "${project.name}"?`)) {
                      deleteMutation.mutate(project.id)
                    }
                  }}
                  className="text-slate-400 hover:text-red-500 p-1.5 rounded-lg hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <h3 className="text-lg font-semibold text-slate-900 mb-1 truncate">{project.name}</h3>
              <p className="text-sm text-slate-500 mb-4 line-clamp-2 min-h-[2.5rem]">
                {project.description || 'No description'}
              </p>

              <button
                onClick={() => navigate(`/projects/${project.id}/datasets`)}
                className="flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
              >
                View Datasets
                <ArrowRight size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <>
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50" onClick={() => setShowModal(false)} />
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-2xl border border-slate-200 p-6 max-w-md w-full">
              <h2 className="text-xl font-bold text-slate-900 mb-4">Create New Project</h2>
              <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate(formData) }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Project Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="My Data Project"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Description (optional)
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Brief description of this project..."
                    rows={3}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="flex-1 px-4 py-2 text-sm font-medium bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition-colors disabled:opacity-50"
                  >
                    {createMutation.isPending ? 'Creating...' : 'Create Project'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ProjectsPage
