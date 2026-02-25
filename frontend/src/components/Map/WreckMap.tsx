import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { Wreck } from '../../types'

// Fix default marker icons in Leaflet + Vite
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const wreckIcon = new L.Icon({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
  className: 'wreck-marker',
})

// Ouistreham port
const OUISTREHAM: [number, number] = [49.2833, -0.25]

interface Props {
  wrecks: Wreck[]
  selectedWreck: Wreck | null
  onSelectWreck: (wreck: Wreck) => void
  onBoundsChange: (bounds: { minLat: number; maxLat: number; minLon: number; maxLon: number }) => void
}

function BoundsWatcher({ onBoundsChange }: { onBoundsChange: Props['onBoundsChange'] }) {
  const map = useMap()

  useEffect(() => {
    const handler = () => {
      const b = map.getBounds()
      onBoundsChange({
        minLat: b.getSouth(),
        maxLat: b.getNorth(),
        minLon: b.getWest(),
        maxLon: b.getEast(),
      })
    }

    map.on('moveend', handler)
    // Initial load
    handler()

    return () => {
      map.off('moveend', handler)
    }
  }, [map, onBoundsChange])

  return null
}

function FlyToWreck({ wreck }: { wreck: Wreck | null }) {
  const map = useMap()

  useEffect(() => {
    if (wreck) {
      map.flyTo([wreck.latitude, wreck.longitude], 14, { duration: 1 })
    }
  }, [map, wreck])

  return null
}

export default function WreckMap({ wrecks, selectedWreck, onSelectWreck, onBoundsChange }: Props) {
  return (
    <MapContainer
      center={OUISTREHAM}
      zoom={11}
      className="h-full w-full"
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <BoundsWatcher onBoundsChange={onBoundsChange} />
      <FlyToWreck wreck={selectedWreck} />

      {wrecks.map((wreck) => (
        <Marker
          key={wreck.id}
          position={[wreck.latitude, wreck.longitude]}
          icon={wreckIcon}
          eventHandlers={{
            click: () => onSelectWreck(wreck),
          }}
        >
          <Popup>
            <div className="text-sm min-w-48">
              <p className="font-bold text-base mb-1">
                {wreck.name || 'Inconnue'}
              </p>
              {wreck.depth != null && (
                <p className="text-gray-600">
                  Brassiage: <strong>{wreck.depth}m</strong> (sonde)
                </p>
              )}
              {wreck.object_length != null && (
                <p className="text-gray-600">
                  Longueur: {wreck.object_length}m
                </p>
              )}
              {wreck.ship_info && (
                <p className="text-gray-600 mt-1">{wreck.ship_info}</p>
              )}
              {wreck.sinking_circumstances && (
                <p className="text-gray-500 text-xs mt-1 italic">
                  {wreck.sinking_circumstances}
                </p>
              )}
              <p className="text-gray-400 text-xs mt-2">
                {wreck.latitude.toFixed(4)}°N, {wreck.longitude.toFixed(4)}°
                {wreck.longitude >= 0 ? 'E' : 'W'}
              </p>
              {wreck.distance_nm != null && (
                <p className="text-blue-600 text-xs">
                  {wreck.distance_nm} NM — {wreck.bearing}°
                </p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
