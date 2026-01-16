"use client"

import React, { createContext, useContext, useState, useCallback, useEffect } from "react"
import axios from "axios"
import { useSession } from "@/lib/auth-client"

interface Task {
  id: number
  title: string
  description: string | null
  status: string
}

interface TaskContextType {
  tasks: Task[]
  loading: boolean
  refreshTasks: () => Promise<void>
  setTasks: React.Dispatch<React.SetStateAction<Task[]>>
}

const TaskContext = createContext<TaskContextType | undefined>(undefined)

export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const { data: session } = useSession()

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

  const refreshTasks = useCallback(async () => {
    if (!session?.session?.token) return

    try {
      const response = await axios.get<Task[]>(`${API_URL}/tasks/`, {
        headers: {
          Authorization: `Bearer ${session.session.token}`,
        },
      })
      setTasks(response.data)
    } catch (error) {
      console.error("[TaskContext] Failed to fetch tasks:", error)
    } finally {
      setLoading(false)
    }
  }, [session?.session?.token, API_URL])

  useEffect(() => {
    if (session) {
      refreshTasks()
    }
  }, [session, refreshTasks])

  return <TaskContext.Provider value={{ tasks, loading, refreshTasks, setTasks }}>{children}</TaskContext.Provider>
}

export function useTasks() {
  const context = useContext(TaskContext)
  if (context === undefined) {
    throw new Error("useTasks must be used within a TaskProvider")
  }
  return context
}