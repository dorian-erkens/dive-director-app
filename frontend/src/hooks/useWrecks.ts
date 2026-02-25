import { useCallback, useState } from 'react'
import type { Wreck } from '../types'

export function useWrecks() {
  const [wrecks, setWrecks] = useState<Wreck[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedWreck, setSelectedWreck] = useState<Wreck | null>(null)

  const fetchNearby = useCallback(
    async (lat: number, lon: number, radius: number = 10) => {
      setLoading(true)
      try {
        const res = await fetch(
          `/api/wrecks/nearby?lat=${lat}&lon=${lon}&radius=${radius}&limit=200`,
        )
        const data = await res.json()
        setWrecks(data.wrecks)
      } catch (err) {
        console.error('Failed to fetch wrecks:', err)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const fetchBbox = useCallback(
    async (minLat: number, maxLat: number, minLon: number, maxLon: number) => {
      setLoading(true)
      try {
        const res = await fetch(
          `/api/wrecks/bbox?min_lat=${minLat}&max_lat=${maxLat}&min_lon=${minLon}&max_lon=${maxLon}&limit=300`,
        )
        const data = await res.json()
        setWrecks(data.wrecks)
      } catch (err) {
        console.error('Failed to fetch wrecks:', err)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const searchByName = useCallback(async (name: string) => {
    setLoading(true)
    try {
      const res = await fetch(`/api/wrecks/search?name=${encodeURIComponent(name)}`)
      const data = await res.json()
      setWrecks(data.wrecks)
    } catch (err) {
      console.error('Failed to search wrecks:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    wrecks,
    loading,
    selectedWreck,
    setSelectedWreck,
    fetchNearby,
    fetchBbox,
    searchByName,
  }
}
