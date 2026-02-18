'use client'

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { BarChart3, FileText, TrendingUp, Activity } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<any>(null)

  useEffect(() => {
    // Check API Gateway health
    axios.get(`${API_URL}/health`)
      .then(res => setHealthStatus(res.data))
      .catch(err => {
        console.error('Health check failed:', err)
        setHealthStatus({ status: 'error' })
      })
  }, [])

  const { data: servicesHealth } = useQuery({
    queryKey: ['services-health'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/health/services`)
      return res.data
    },
    enabled: !!healthStatus,
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">GHDA-SaaS Admin Dashboard</h1>

        {/* Health Status */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">System Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <HealthCard
              title="API Gateway"
              status={healthStatus?.status === 'healthy' ? 'healthy' : 'error'}
              icon={<Activity className="w-6 h-6" />}
            />
            {servicesHealth?.services && Object.entries(servicesHealth.services).map(([name, status]: [string, any]) => (
              <HealthCard
                key={name}
                title={name.replace('-service', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                status={status?.status === 'healthy' ? 'healthy' : 'error'}
                icon={<Activity className="w-6 h-6" />}
              />
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Quick Stats</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Reports"
              value="0"
              icon={<FileText className="w-8 h-8" />}
              color="blue"
            />
            <StatCard
              title="Total Documents"
              value="0"
              icon={<FileText className="w-8 h-8" />}
              color="green"
            />
            <StatCard
              title="Analytics"
              value="0"
              icon={<TrendingUp className="w-8 h-8" />}
              color="purple"
            />
            <StatCard
              title="Processing"
              value="0"
              icon={<BarChart3 className="w-8 h-8" />}
              color="orange"
            />
          </div>
        </div>

        {/* Services Overview */}
        <div>
          <h2 className="text-2xl font-semibold mb-4">Services Overview</h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <p className="text-gray-600 dark:text-gray-400">
              Welcome to the GHDA-SaaS Admin Dashboard. Use the navigation to explore different sections.
            </p>
            <div className="mt-4 space-y-2">
              <p className="text-sm text-gray-500">
                • <strong>Document Service</strong>: Upload and manage documents
              </p>
              <p className="text-sm text-gray-500">
                • <strong>Report Service</strong>: View and export reports
              </p>
              <p className="text-sm text-gray-500">
                • <strong>Analytics Service</strong>: View analytics and trends
              </p>
              <p className="text-sm text-gray-500">
                • <strong>Processing Service</strong>: Monitor document processing
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

function HealthCard({ title, status, icon }: { title: string; status: string; icon: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
          <p className={`text-lg font-semibold mt-1 ${
            status === 'healthy' ? 'text-green-600' : 'text-red-600'
          }`}>
            {status === 'healthy' ? 'Healthy' : 'Error'}
          </p>
        </div>
        <div className={`p-3 rounded-full ${
          status === 'healthy' ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }: { title: string; value: string; icon: React.ReactNode; color: string }) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}
