import { useState, useCallback, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  FolderOpen, Database, BarChart3, MessageSquare,
  ArrowRight, Plus, FileText, TrendingUp,
  MoreHorizontal, Eye, Trash2, Upload, UploadCloud,
} from 'lucide-react'
import api from '../services/api'

/* ── Types ── */
interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
}

interface Dataset {
  id: number
  name: string
  file_type: string
  file_size: number
  project_id: number
  created_at: string
  metadata?: { rows: number; columns: number }
}

/* ── Helpers ── */
const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

const FILE_TYPE_STYLE: Record<string, string> = {
  csv:     'badge-csv',
  xlsx:    'badge-xlsx',
  xls:     'badge-xls',
  json:    'badge-json',
  parquet: 'badge-parquet',
}

/* ══════════════════════════════════════════════
   DashboardPage
══════════════════════════════════════════════ */
const DashboardPage = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // ── Data fetching ──
  const { data: projects = [], isLoading: loadingProjects } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => (await api.get('/projects')).data,
  })

  const { data: allDatasets = [], isLoading: loadingDatasets } = useQuery<Dataset[]>({
    queryKey: ['all-datasets', projects.map((p) => p.id)],
    queryFn: async () => {
      if (projects.length === 0) return []
      const results = await Promise.all(
        projects.map((p) => api.get(`/datasets/project/${p.id}`).then((r) => r.data as Dataset[]))
      )
      return results.flat()
    },
    enabled: projects.length > 0,
  })

  const isLoading = loadingProjects || loadingDatasets

  // ── Derived data ──
  const recentDatasets = [...allDatasets]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 8)

  const recentProjects = [...projects]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  const totalStorage = allDatasets.reduce((s, d) => s + d.file_size, 0)
  const datasetsWithMeta = allDatasets.filter((d) => d.metadata?.rows)
  const avgRows =
    datasetsWithMeta.length > 0
      ? Math.round(datasetsWithMeta.reduce((s, d) => s + (d.metadata?.rows ?? 0), 0) / datasetsWithMeta.length)
      : 0
  const largestDataset = datasetsWithMeta.reduce<Dataset | undefined>(
    (max, d) => ((d.metadata?.rows ?? 0) > (max?.metadata?.rows ?? 0) ? d : max),
    datasetsWithMeta[0]
  )

  // ── Dataset delete ──
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/datasets/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['all-datasets'] })
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  // ── Drag & drop upload ──
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProjectId, setUploadProjectId] = useState<number | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'done' | 'error'>('idle')
  const dragCounter = useRef(0)

  const uploadMutation = useMutation({
    mutationFn: async ({ file, projectId }: { file: File; projectId: number }) => {
      const form = new FormData()
      form.append('file', file)
      form.append('project_id', String(projectId))
      return (await api.post('/datasets', form)).data
    },
    onSuccess: () => {
      setUploadStatus('done')
      queryClient.invalidateQueries({ queryKey: ['all-datasets'] })
      setTimeout(() => setUploadStatus('idle'), 2500)
    },
    onError: () => {
      setUploadStatus('error')
      setTimeout(() => setUploadStatus('idle'), 3000)
    },
  })

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      dragCounter.current = 0
      setIsDragOver(false)
      const file = e.dataTransfer.files[0]
      if (!file) return
      const ext = file.name.split('.').pop()?.toLowerCase()
      if (!['csv', 'xlsx', 'xls', 'json', 'parquet'].includes(ext ?? '')) {
        setUploadStatus('error')
        setTimeout(() => setUploadStatus('idle'), 3000)
        return
      }
      const targetProject = uploadProjectId ?? projects[0]?.id
      if (!targetProject) return
      setUploadStatus('uploading')
      uploadMutation.mutate({ file, projectId: targetProject })
    },
    [uploadProjectId, projects, uploadMutation]
  )

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    dragCounter.current++
    setIsDragOver(true)
  }
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    dragCounter.current--
    if (dragCounter.current === 0) setIsDragOver(false)
  }

  return (
    <div
      className="space-y-6"
      onDragEnter={handleDragEnter}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* ── Page header ── */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-0.5">Overview of your data projects and datasets</p>
      </div>

      {/* ── Stat cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Projects"          value={isLoading ? '—' : projects.length}            icon={<FolderOpen size={20}/>}  color="indigo"  onClick={() => navigate('/projects')} />
        <StatCard label="Datasets"          value={isLoading ? '—' : allDatasets.length}          icon={<Database size={20}/>}    color="cyan"    onClick={() => navigate('/projects')} />
        <StatCard label="Avg Rows / Dataset" value={isLoading ? '—' : avgRows > 0 ? avgRows.toLocaleString() : '—'} icon={<TrendingUp size={20}/>}  color="violet" subtitle={largestDataset ? `Largest: ${largestDataset.metadata!.rows.toLocaleString()} rows` : undefined} />
        <StatCard label="Total Storage"     value={isLoading ? '—' : formatSize(totalStorage)}   icon={<FileText size={20}/>}    color="emerald" subtitle={largestDataset ? `Largest: ${largestDataset.name}` : undefined} />
      </div>

      {/* ── Drag & drop dropzone (shown when dragging) ── */}
      {(isDragOver || uploadStatus !== 'idle') && (
        <div
          className={`rounded-xl border-2 border-dashed px-6 py-8 flex flex-col items-center justify-center gap-3 transition-all ${
            uploadStatus === 'error'
              ? 'border-red-400 bg-red-50'
              : uploadStatus === 'done'
              ? 'border-emerald-400 bg-emerald-50'
              : 'dropzone-active border-indigo-400'
          }`}
        >
          <UploadCloud size={36} className={
            uploadStatus === 'error' ? 'text-red-400'
            : uploadStatus === 'done' ? 'text-emerald-500'
            : 'text-indigo-400'
          } />
          <div className="text-center">
            {uploadStatus === 'uploading' && <p className="text-sm font-medium text-indigo-600">Uploading…</p>}
            {uploadStatus === 'done'      && <p className="text-sm font-medium text-emerald-600">Upload complete!</p>}
            {uploadStatus === 'error'     && <p className="text-sm font-medium text-red-600">Unsupported file or no project available.</p>}
            {uploadStatus === 'idle'      && (
              <>
                <p className="text-sm font-semibold text-indigo-700">Drop file to upload</p>
                <p className="text-xs text-slate-400 mt-0.5">CSV, Excel, JSON, Parquet supported</p>
                {projects.length > 1 && (
                  <div className="mt-3">
                    <select
                      value={uploadProjectId ?? projects[0]?.id ?? ''}
                      onChange={(e) => setUploadProjectId(Number(e.target.value))}
                      className="text-xs border border-slate-200 rounded px-2 py-1 bg-white"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Main grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Left: Recent datasets (3/5) */}
        <div className="lg:col-span-3 bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-800">Recent Datasets</h2>
            <button onClick={() => navigate('/projects')} className="text-xs text-indigo-500 hover:text-indigo-600 flex items-center gap-1 font-medium">
              View all <ArrowRight size={12}/>
            </button>
          </div>

          {isLoading ? (
            <div className="p-5 space-y-3">
              {[...Array(4)].map((_, i) => <div key={i} className="h-11 bg-slate-100 rounded-lg animate-pulse"/>)}
            </div>
          ) : recentDatasets.length === 0 ? (
            <DropEmptyState onAction={() => navigate('/projects')} />
          ) : (
            <div className="divide-y divide-slate-50">
              {recentDatasets.map((dataset) => {
                const project = projects.find((p) => p.id === dataset.project_id)
                return (
                  <DatasetRow
                    key={dataset.id}
                    dataset={dataset}
                    projectName={project?.name}
                    onView={() => navigate(`/datasets/${dataset.id}`)}
                    onVisualize={() => navigate(`/datasets/${dataset.id}/visualizations`)}
                    onChat={() => navigate(`/datasets/${dataset.id}/chat`)}
                    onDelete={() => deleteMutation.mutate(dataset.id)}
                  />
                )
              })}
            </div>
          )}
        </div>

        {/* Right column (2/5) */}
        <div className="lg:col-span-2 flex flex-col gap-6">

          {/* Recent Projects */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
              <h2 className="text-sm font-semibold text-slate-800">Recent Projects</h2>
              <button onClick={() => navigate('/projects')} className="text-xs text-indigo-500 hover:text-indigo-600 flex items-center gap-1 font-medium">
                View all <ArrowRight size={12}/>
              </button>
            </div>

            {isLoading ? (
              <div className="p-4 space-y-2.5">
                {[...Array(3)].map((_, i) => <div key={i} className="h-10 bg-slate-100 rounded-lg animate-pulse"/>)}
              </div>
            ) : recentProjects.length === 0 ? (
              <div className="flex flex-col items-center py-8 px-4 text-center">
                <FolderOpen size={28} className="text-slate-300 mb-2"/>
                <p className="text-slate-400 text-xs">No projects yet</p>
                <button onClick={() => navigate('/projects')} className="mt-3 text-xs text-indigo-500 font-medium hover:underline">
                  Create your first project →
                </button>
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {recentProjects.map((project) => {
                  const count = allDatasets.filter((d) => d.project_id === project.id).length
                  return (
                    <div
                      key={project.id}
                      onClick={() => navigate(`/projects/${project.id}/datasets`)}
                      className="flex items-center gap-3 px-5 py-3 hover:bg-slate-50 cursor-pointer transition-colors group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
                        <FolderOpen size={14} className="text-indigo-500"/>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{project.name}</p>
                        <p className="text-xs text-slate-400">{count} dataset{count !== 1 ? 's' : ''}</p>
                      </div>
                      <ArrowRight size={13} className="text-slate-300 group-hover:text-slate-400 flex-shrink-0"/>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* AI Quick Actions */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100">
              <h2 className="text-sm font-semibold text-slate-800">Quick Actions</h2>
            </div>
            <div className="p-4 space-y-2.5">
              <button
                onClick={() => navigate('/projects')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-50 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-200 transition-all group text-left"
              >
                <div className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
                  <Plus size={15} className="text-indigo-600"/>
                </div>
                <span className="text-sm font-medium text-slate-700 group-hover:text-indigo-700">New Project</span>
                <ArrowRight size={13} className="text-slate-300 ml-auto group-hover:text-indigo-400"/>
              </button>

              {recentDatasets[0] && (
                <>
                  <button
                    onClick={() => navigate(`/datasets/${recentDatasets[0].id}/visualizations`)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-50 hover:bg-cyan-50 border border-slate-200 hover:border-cyan-200 transition-all group text-left"
                  >
                    <div className="w-8 h-8 rounded-lg bg-cyan-100 flex items-center justify-center flex-shrink-0">
                      <BarChart3 size={15} className="text-cyan-600"/>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-700 group-hover:text-cyan-700">Visualize Dataset</p>
                      <p className="text-xs text-slate-400 truncate">{recentDatasets[0].name}</p>
                    </div>
                    <ArrowRight size={13} className="text-slate-300 ml-auto group-hover:text-cyan-400"/>
                  </button>

                  <button
                    onClick={() => navigate(`/datasets/${recentDatasets[0].id}/chat`)}
                    className="ai-glow w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gradient-to-r from-indigo-50 to-violet-50 border border-indigo-200 hover:from-indigo-100 hover:to-violet-100 transition-all group text-left"
                  >
                    <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center flex-shrink-0 shadow-sm">
                      <MessageSquare size={15} className="text-white"/>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-indigo-700">Chat with AI</p>
                      <p className="text-xs text-indigo-400 truncate">{recentDatasets[0].name}</p>
                    </div>
                    <ArrowRight size={13} className="text-indigo-300 ml-auto group-hover:text-indigo-500"/>
                  </button>
                </>
              )}

              {/* Drop hint when no datasets */}
              {allDatasets.length === 0 && !isLoading && (
                <div className="flex items-center gap-3 px-4 py-3 rounded-lg border-2 border-dashed border-slate-200 text-slate-400">
                  <Upload size={15}/>
                  <span className="text-xs">Drag & drop a file anywhere to upload</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════
   DatasetRow
══════════════════════════════════════════════ */
interface DatasetRowProps {
  dataset: Dataset
  projectName?: string
  onView: () => void
  onVisualize: () => void
  onChat: () => void
  onDelete: () => void
}

const DatasetRow = ({ dataset, projectName, onView, onVisualize, onChat, onDelete }: DatasetRowProps) => {
  const [menuOpen, setMenuOpen] = useState(false)
  const badgeClass = FILE_TYPE_STYLE[dataset.file_type] ?? 'bg-slate-100 text-slate-600'

  return (
    <div
      className="flex items-center gap-3 px-5 py-3.5 hover:bg-slate-50 cursor-pointer transition-colors group relative"
      onClick={onView}
    >
      {/* Icon */}
      <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
        <Database size={15} className="text-indigo-500"/>
      </div>

      {/* Name + meta */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-800 truncate">{dataset.name}</p>
        <p className="text-xs text-slate-400 mt-0.5 truncate">
          {projectName ?? '—'} · {formatSize(dataset.file_size)}
          {dataset.metadata && <> · {dataset.metadata.rows.toLocaleString()} rows</>}
        </p>
      </div>

      {/* File type badge */}
      <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded uppercase ${badgeClass} flex-shrink-0`}>
        {dataset.file_type}
      </span>

      {/* Date */}
      <span className="text-xs text-slate-400 flex-shrink-0 hidden sm:block">{formatDate(dataset.created_at)}</span>

      {/* ··· menu */}
      <div className="relative flex-shrink-0" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => setMenuOpen((v) => !v)}
          className="w-7 h-7 rounded-md flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 opacity-0 group-hover:opacity-100 transition-all"
        >
          <MoreHorizontal size={15}/>
        </button>
        {menuOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)}/>
            <div className="absolute right-0 top-8 z-20 w-44 bg-white rounded-lg shadow-lg border border-slate-200 py-1 text-sm">
              <MenuItem icon={<Eye size={13}/>}       label="View & Analyze" onClick={() => { setMenuOpen(false); onView() }}     />
              <MenuItem icon={<BarChart3 size={13}/>} label="Visualize"      onClick={() => { setMenuOpen(false); onVisualize() }} />
              <MenuItem icon={<MessageSquare size={13}/>} label="Chat with AI" onClick={() => { setMenuOpen(false); onChat() }}  />
              <div className="my-1 border-t border-slate-100"/>
              <MenuItem icon={<Trash2 size={13}/>}    label="Delete"         onClick={() => { setMenuOpen(false); onDelete() }}    danger />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

const MenuItem = ({ icon, label, onClick, danger }: { icon: React.ReactNode; label: string; onClick: () => void; danger?: boolean }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-2.5 px-3 py-1.5 hover:bg-slate-50 transition-colors text-left ${danger ? 'text-red-500 hover:bg-red-50' : 'text-slate-700'}`}
  >
    {icon}{label}
  </button>
)

/* ══════════════════════════════════════════════
   StatCard
══════════════════════════════════════════════ */
type CardColor = 'indigo' | 'cyan' | 'violet' | 'emerald'

const COLOR_MAP: Record<CardColor, { bg: string; icon: string; border: string }> = {
  indigo:  { bg: 'bg-indigo-50',  icon: 'text-indigo-500',  border: 'border-indigo-100' },
  cyan:    { bg: 'bg-cyan-50',    icon: 'text-cyan-500',    border: 'border-cyan-100'   },
  violet:  { bg: 'bg-violet-50',  icon: 'text-violet-500',  border: 'border-violet-100' },
  emerald: { bg: 'bg-emerald-50', icon: 'text-emerald-500', border: 'border-emerald-100'},
}

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  color: CardColor
  subtitle?: string
  onClick?: () => void
}

const StatCard = ({ label, value, icon, color, subtitle, onClick }: StatCardProps) => {
  const c = COLOR_MAP[color]
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border ${c.border} shadow-card p-5 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-400 mt-1 truncate" title={subtitle}>{subtitle}</p>}
        </div>
        <div className={`w-9 h-9 rounded-lg ${c.bg} ${c.icon} flex items-center justify-center flex-shrink-0`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════
   DropEmptyState
══════════════════════════════════════════════ */
const DropEmptyState = ({ onAction }: { onAction: () => void }) => (
  <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
    <div className="w-14 h-14 rounded-xl bg-indigo-50 flex items-center justify-center mb-3">
      <Upload size={22} className="text-indigo-400"/>
    </div>
    <p className="text-slate-600 text-sm font-medium">No datasets yet</p>
    <p className="text-slate-400 text-xs mt-1">Drag & drop a file here, or go to a project to upload</p>
    <button onClick={onAction} className="mt-4 text-sm text-indigo-500 font-medium hover:underline">
      Go to Projects →
    </button>
  </div>
)

export default DashboardPage
