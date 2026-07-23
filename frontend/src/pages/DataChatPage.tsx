import { useState, useRef, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Send, Trash2, Code, TrendingUp } from 'lucide-react'
import api from '../services/api'

interface Dataset {
  id: number
  name: string
}

interface ChatMessage {
  id?: number
  question: string
  answer: string
  code?: string
  result?: any
  result_type?: string
  chart_config?: any
  error?: string
  timestamp: string
}

const DataChatPage = () => {
  const { datasetId } = useParams()
  const queryClient = useQueryClient()
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [showCode, setShowCode] = useState<{ [key: number]: boolean }>({})
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: dataset } = useQuery<Dataset>({
    queryKey: ['dataset', datasetId],
    queryFn: async () => {
      const response = await api.get(`/datasets/${datasetId}`)
      return response.data
    }
  })

  const { data: history } = useQuery({
    queryKey: ['chat-history', datasetId],
    queryFn: async () => {
      const response = await api.get(`/chat/history/${datasetId}`)
      return response.data
    }
  })

  useEffect(() => {
    if (history && history.length > 0) {
      const formattedHistory = history.reverse().map((item: any) => ({
        id: item.id,
        question: item.question,
        answer: item.answer,
        code: item.code,
        timestamp: item.created_at
      }))
      setMessages(formattedHistory)
    }
  }, [history])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const chatMutation = useMutation({
    mutationFn: async (question: string) => {
      const response = await api.post('/chat/ask', {
        dataset_id: parseInt(datasetId!),
        question,
        save_history: true
      })
      return response.data
    },
    onSuccess: (data) => {
      const newMessage: ChatMessage = {
        question: question,
        answer: data.answer,
        code: data.code,
        result: data.result,
        result_type: data.result_type,
        chart_config: data.chart_config,
        error: data.error,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, newMessage])
      setQuestion('')
      queryClient.invalidateQueries({ queryKey: ['chat-history', datasetId] })
    },
    onError: (error: any) => {
      const errorMessage: ChatMessage = {
        question: question,
        answer: error.response?.data?.detail || 'An error occurred',
        error: 'ERROR',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
      setQuestion('')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() || chatMutation.isPending) return
    chatMutation.mutate(question)
  }

  const handleClearHistory = async () => {
    if (window.confirm('Clear all chat history?')) {
      setMessages([])
      queryClient.invalidateQueries({ queryKey: ['chat-history', datasetId] })
    }
  }

  const toggleCode = (index: number) => {
    setShowCode(prev => ({ ...prev, [index]: !prev[index] }))
  }

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Chat with Data</h1>
          {dataset && (
            <p className="text-gray-600 mt-1">Dataset: {dataset.name}</p>
          )}
        </div>
        <button
          onClick={handleClearHistory}
          disabled={messages.length === 0}
          className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
        >
          <Trash2 size={16} />
          Clear History
        </button>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 bg-white rounded-lg shadow overflow-y-auto p-6 space-y-6 mb-4">
        {messages.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <TrendingUp size={48} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">Ask me anything about your data!</p>
            <div className="mt-6 space-y-2 text-sm">
              <p className="text-gray-600">Example questions:</p>
              <div className="flex flex-col gap-2 max-w-md mx-auto">
                <button
                  onClick={() => setQuestion("What is the average value of all numeric columns?")}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-left"
                >
                  "What is the average value of all numeric columns?"
                </button>
                <button
                  onClick={() => setQuestion("How many unique values are in each column?")}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-left"
                >
                  "How many unique values are in each column?"
                </button>
                <button
                  onClick={() => setQuestion("Show me the top 5 rows sorted by the first numeric column")}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-left"
                >
                  "Show me the top 5 rows"
                </button>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className="space-y-3">
            {/* Question */}
            <div className="flex justify-end">
              <div className="bg-blue-600 text-white px-4 py-3 rounded-lg max-w-[70%]">
                <p>{msg.question}</p>
              </div>
            </div>

            {/* Answer */}
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-3 rounded-lg max-w-[70%] space-y-3">
                <p className="text-gray-900 whitespace-pre-wrap">{msg.answer}</p>

                {/* Error */}
                {msg.error && msg.error !== 'ERROR' && (
                  <div className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded">
                    Error: {msg.error}
                  </div>
                )}

                {/* Code */}
                {msg.code && (
                  <div>
                    <button
                      onClick={() => toggleCode(index)}
                      className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                    >
                      <Code size={14} />
                      {showCode[index] ? 'Hide' : 'Show'} Code
                    </button>
                    {showCode[index] && (
                      <pre className="mt-2 bg-gray-900 text-green-400 p-3 rounded text-xs overflow-x-auto">
                        {msg.code}
                      </pre>
                    )}
                  </div>
                )}

                {/* Result Display */}
                {msg.result && msg.result_type && (
                  <div className="mt-3">
                    {msg.result_type === 'scalar' && (
                      <div className="text-2xl font-bold text-blue-600">
                        {msg.result}
                      </div>
                    )}

                    {msg.result_type === 'series' && typeof msg.result === 'object' && (
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-sm border">
                          <tbody>
                            {Object.entries(msg.result).map(([key, value]: [string, any]) => (
                              <tr key={key} className="border-b">
                                <td className="px-3 py-2 font-medium bg-gray-50">{key}</td>
                                <td className="px-3 py-2">{String(value)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {msg.result_type === 'dataframe' && Array.isArray(msg.result) && msg.result.length > 0 && (
                      <div className="overflow-x-auto">
                        <table className="min-w-full text-sm border">
                          <thead className="bg-gray-50">
                            <tr>
                              {Object.keys(msg.result[0]).map(key => (
                                <th key={key} className="px-3 py-2 text-left font-medium border-b">
                                  {key}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.result.map((row: any, idx: number) => (
                              <tr key={idx} className="border-b">
                                {Object.values(row).map((val: any, vidx: number) => (
                                  <td key={vidx} className="px-3 py-2">
                                    {String(val)}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {msg.result_type === 'list' && Array.isArray(msg.result) && (
                      <div className="space-y-1">
                        {msg.result.map((item: any, idx: number) => (
                          <div key={idx} className="px-3 py-1 bg-white rounded text-sm">
                            {String(item)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Chart */}
                {msg.chart_config && (
                  <div className="mt-3 p-4 bg-white rounded border">
                    <h4 className="font-medium mb-3">{msg.chart_config.title}</h4>
                    <div className="space-y-2">
                      {msg.chart_config.data.labels.map((label: string, idx: number) => {
                        const value = msg.chart_config.data.values[idx]
                        const maxValue = Math.max(...msg.chart_config.data.values)
                        const percentage = (value / maxValue) * 100
                        
                        return (
                          <div key={idx} className="flex items-center gap-3">
                            <div className="w-24 text-sm truncate">{label}</div>
                            <div className="flex-1">
                              <div className="bg-gray-200 rounded-full h-6 relative">
                                <div
                                  className="bg-blue-600 rounded-full h-6 flex items-center justify-end px-2"
                                  style={{ width: `${percentage}%` }}
                                >
                                  <span className="text-xs text-white font-medium">{value}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                <div className="text-xs text-gray-500">
                  {new Date(msg.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        ))}

        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your data..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={chatMutation.isPending}
          />
          <button
            type="submit"
            disabled={!question.trim() || chatMutation.isPending}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send size={18} />
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default DataChatPage
