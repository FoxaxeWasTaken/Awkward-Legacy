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

      const parts = []
      if (data.husband) {
        parts.push(`${data.husband.first_name} ${data.husband.last_name}`)
      }
      if (data.wife) {
        parts.push(`${data.wife.first_name} ${data.wife.last_name}`)
      }
      familyTitle.value = parts.length > 0 ? parts.join(' & ') : 'Family Tree'
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

  const loadCrossFamilyChildren = async (data: FamilyDetailResult) => {
    const childrenMap = new Map<string, Person[]>()
    const processedFamilies = new Set<string>([data.id])
    const loadDescendantFamilies = async (children: Person[]) => {
      for (const child of children) {
        if (child.has_own_family && child.own_families) {
          for (const ownFamily of child.own_families) {
            if (processedFamilies.has(ownFamily.id)) continue
            processedFamilies.add(ownFamily.id)

            try {
              const familyDetail = await apiService.getFamilyDetail(ownFamily.id)
              const familyChildren = familyDetail.children
                .map((c) => c.person)
                .filter(Boolean) as Person[]
              childrenMap.set(ownFamily.id, familyChildren)

              if (familyChildren.length > 0) {
                await loadDescendantFamilies(familyChildren)
              }
            } catch (err) {
              console.error(`Error loading children for family ${ownFamily.id}:`, err)
            }
          }
        }
      }
    }
    const rootChildren = data.children.map((c) => c.person).filter(Boolean) as Person[]
    await loadDescendantFamilies(rootChildren)

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
