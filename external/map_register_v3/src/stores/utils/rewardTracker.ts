import type * as API2 from '@/api/alova/globals'
import type { Coordinate2D, GSMarkerInfo } from '@/packages/map'

export interface RewardTrackerAmount {
  found?: boolean
  value?: number
  score?: number
}

export interface RewardTrackerMatch {
  template?: string
  score?: number
  scale?: number
  amount?: RewardTrackerAmount
}

export interface RewardTrackerPayload {
  tracker?: {
    available?: boolean
    position?: {
      x?: number
      y?: number
      mapId?: number
    }
  }
  matches?: RewardTrackerMatch[]
}

export interface FindNearestMarkerOptions<T extends API2.MarkerVo | GSMarkerInfo> {
  position: Coordinate2D
  markers: T[]
  excludeMarkerIds?: Set<number>
  maxDistance?: number
  predicate?: (marker: T) => boolean
}

export interface NearestMarkerResult<T extends API2.MarkerVo | GSMarkerInfo> {
  marker: T
  position: Coordinate2D
  distance: number
}

export interface RewardTrackerLinkResult<T extends API2.MarkerVo | GSMarkerInfo> extends NearestMarkerResult<T> {
  amount?: number
  rewardMatch?: RewardTrackerMatch
}

const isRenderMarker = (marker: API2.MarkerVo | GSMarkerInfo): marker is GSMarkerInfo => {
  return 'render' in marker
}

const getMarkerPosition = (marker: API2.MarkerVo | GSMarkerInfo): Coordinate2D | undefined => {
  if (isRenderMarker(marker))
    return marker.render.position

  if (!marker.position)
    return

  const [x, y] = marker.position.split(',').map(Number)
  if (!Number.isFinite(x) || !Number.isFinite(y))
    return

  return [x, y]
}

export const findNearestMarkerByPosition = <T extends API2.MarkerVo | GSMarkerInfo>({
  position,
  markers,
  excludeMarkerIds,
  maxDistance = Number.POSITIVE_INFINITY,
  predicate,
}: FindNearestMarkerOptions<T>): NearestMarkerResult<T> | undefined => {
  const [targetX, targetY] = position
  let bestResult: NearestMarkerResult<T> | undefined
  let bestDistanceSq = maxDistance ** 2

  for (const marker of markers) {
    const { id } = marker
    if (id !== undefined && excludeMarkerIds?.has(id))
      continue
    if (predicate && !predicate(marker))
      continue

    const markerPosition = getMarkerPosition(marker)
    if (!markerPosition)
      continue

    const [markerX, markerY] = markerPosition
    const distanceSq = (markerX - targetX) ** 2 + (markerY - targetY) ** 2
    if (distanceSq > bestDistanceSq)
      continue

    bestDistanceSq = distanceSq
    bestResult = {
      marker,
      position: markerPosition,
      distance: Math.sqrt(distanceSq),
    }
  }

  return bestResult
}

export const linkRewardEventToNearestMarker = <T extends API2.MarkerVo | GSMarkerInfo>(
  event: RewardTrackerPayload,
  options: Omit<FindNearestMarkerOptions<T>, 'position'>,
): RewardTrackerLinkResult<T> | undefined => {
  const trackerX = event.tracker?.position?.x
  const trackerY = event.tracker?.position?.y
  if (!event.tracker?.available || !Number.isFinite(trackerX) || !Number.isFinite(trackerY))
    return

  const rewardMatch = [...(event.matches ?? [])]
    .filter(match => match.template === 'primogem')
    .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))[0]

  const nearest = findNearestMarkerByPosition({
    ...options,
    position: [trackerX, trackerY],
  })
  if (!nearest)
    return

  return {
    ...nearest,
    amount: rewardMatch?.amount?.found ? rewardMatch.amount.value : undefined,
    rewardMatch,
  }
}
