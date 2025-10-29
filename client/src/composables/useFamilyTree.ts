import { ref, watch, type Ref } from 'vue'
import apiService from '../services/api'
import type { FamilyDetailResult, Person } from '../types/family'

export function useFamilyTree(familyId: Ref<string> | string) {
  const isLoading = ref(true)
  const error = ref('')
  const familyData = ref<FamilyDetailResult | null>(null)
  const familyTitle = ref('Family Tree')
  const crossFamilyChildren = ref<Map<string, Person[]>>(new Map())

  const loadFamilyData = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const currentFamilyId = typeof familyId === 'string' ? familyId : familyId.value
      const data = await apiService.getFamilyDetail(currentFamilyId)

      if (!data) {
        throw new Error('No family data received')
      }

      familyData.value = data

      const parts = _extractSpouseNames(data)
      familyTitle.value = _buildFamilyTitle(parts)
      await loadCrossFamilyChildren(data)
    } catch (err: unknown) {
      console.error('Error loading family data:', err)
      const errorMessage =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : 'Failed to load family tree. Please try again.'
      error.value = errorMessage || 'Failed to load family tree. Please try again.'
    } finally {
      isLoading.value = false
    }
  }

  const processFamilyChildren = async (
    familyDetail: FamilyDetailResult,
    childrenMap: Map<string, Person[]>,
  ) => {
    const familyChildren = familyDetail.children.map((c) => c.person).filter(Boolean) as Person[]
    childrenMap.set(familyDetail.id, familyChildren)
    return familyChildren
  }

  const loadFamilyDetailSafely = async (familyId: string, childrenMap: Map<string, Person[]>) => {
    try {
      const familyDetail = await apiService.getFamilyDetail(familyId)
      return await processFamilyChildren(familyDetail, childrenMap)
    } catch (err) {
      console.error(`Error loading children for family ${familyId}:`, err)
      return []
    }
  }

  const processChildFamilies = async (
    child: Person,
    processedFamilies: Set<string>,
    childrenMap: Map<string, Person[]>,
  ) => {
    if (!child.has_own_family || !child.own_families) return

    for (const ownFamily of child.own_families) {
      if (processedFamilies.has(ownFamily.id)) continue
      processedFamilies.add(ownFamily.id)

      const familyChildren = await loadFamilyDetailSafely(ownFamily.id, childrenMap)
      if (familyChildren.length > 0) {
        await loadDescendantFamilies(familyChildren, processedFamilies, childrenMap)
      }
    }
  }

  const loadDescendantFamilies = async (
    children: Person[],
    processedFamilies: Set<string>,
    childrenMap: Map<string, Person[]>,
  ) => {
    for (const child of children) {
      await processChildFamilies(child, processedFamilies, childrenMap)
    }
  }

  const loadCrossFamilyChildren = async (data: FamilyDetailResult) => {
    const childrenMap = new Map<string, Person[]>()
    const processedFamilies = new Set<string>([data.id])
    const rootChildren = data.children.map((c) => c.person).filter(Boolean) as Person[]
    await loadDescendantFamilies(rootChildren, processedFamilies, childrenMap)
    crossFamilyChildren.value = childrenMap
  }

  if (typeof familyId !== 'string') {
    watch(familyId, () => {
      loadFamilyData()
    })
  }

  return {
    isLoading,
    error,
    familyData,
    familyTitle,
    crossFamilyChildren,
    loadFamilyData,
    loadCrossFamilyChildren,
  }
}

function _extractSpouseNames(data: { husband?: { first_name?: string; last_name?: string }; wife?: { first_name?: string; last_name?: string } }): string[] {
  const fullName = (p?: { first_name?: string; last_name?: string }) =>
    ((p?.first_name || '') + ' ' + (p?.last_name || '')).trim()

  return [fullName(data.husband), fullName(data.wife)].filter((n) => !!n)
}

function _buildFamilyTitle(parts: string[]): string {
  if (parts.length === 2) {
    return parts.join(' & ')
  } else if (parts.length === 1) {
    return parts[0]
  } else {
    return 'Family Tree'
  }
}
