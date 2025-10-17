import { ref } from 'vue'
import type { Person, FamilyDetailResult } from '../types/family'
import type { FamilyGeneration } from '../utils/familyUtils'

export function usePersonHighlighting() {
  const hoveredPerson = ref<Person | null>(null)
  const clickedPerson = ref<Person | null>(null)
  const highlightedParents = ref<Set<string>>(new Set())
  const highlightedChildren = ref<Set<string>>(new Set())
  const highlightedSpouse = ref<string | null>(null)

  const selectPerson = (person: Person) => {
    // Toggle off if clicking the same person
    if (clickedPerson.value?.id === person.id) {
      clickedPerson.value = null
      clearHighlights()
    } else {
      clickedPerson.value = person
      // Note: updateHighlights will be called from the component with proper parameters
    }
  }

  const handlePersonHover = (person: Person) => {
    if (!clickedPerson.value) {
      hoveredPerson.value = person
      // Note: updateHighlights will be called from the component with proper parameters
    }
  }

  const handlePersonLeave = () => {
    if (!clickedPerson.value) {
      hoveredPerson.value = null
      clearHighlights()
    }
  }

  const clearHighlights = () => {
    highlightedParents.value = new Set()
    highlightedChildren.value = new Set()
    highlightedSpouse.value = null
  }

  const updateHighlights = (
    person: Person,
    familyData: FamilyDetailResult | null,
    familyGenerations: FamilyGeneration[],
    crossFamilyChildren: Map<string, Person[]>,
  ) => {
    clearHighlights()

    if (!familyData) return

    const parents = new Set<string>()
    const children = new Set<string>()
    let spouse: string | null = null

    // Find parents (check if person is a child in the main family or any sub-family)
    const findParents = (data: FamilyDetailResult) => {
      data.children.forEach((child) => {
        if (child.person?.id === person.id) {
          if (data.husband?.id) parents.add(data.husband.id)
          if (data.wife?.id) parents.add(data.wife.id)
        }
      })
    }

    // Check main family
    findParents(familyData)

    // Check all cross-families
    familyGenerations.forEach((generation) => {
      generation.couples.forEach((couple) => {
        couple.children.forEach((child) => {
          if (child.id === person.id) {
            if (couple.husband?.id) parents.add(couple.husband.id)
            if (couple.wife?.id) parents.add(couple.wife.id)
          }
        })
      })
    })

    // Find spouse (check if person is part of a couple)
    familyGenerations.forEach((generation) => {
      generation.couples.forEach((couple) => {
        if (couple.husband?.id === person.id && couple.wife?.id) {
          spouse = couple.wife.id
        } else if (couple.wife?.id === person.id && couple.husband?.id) {
          spouse = couple.husband.id
        }
      })
    })

    // Recursively find all descendants (children, grandchildren, etc.)
    const findAllDescendants = (personToCheck: Person) => {
      if (personToCheck.has_own_family && personToCheck.own_families) {
        personToCheck.own_families.forEach((ownFamily) => {
          const familyChildren = crossFamilyChildren.get(ownFamily.id) || []
          familyChildren.forEach((child) => {
            if (child.id && !children.has(child.id)) {
              children.add(child.id)
              // Recursively find this child's descendants
              findAllDescendants(child)
            }
          })
        })
      }
    }

    // Start recursive search from the selected person
    findAllDescendants(person)

    highlightedParents.value = parents
    highlightedChildren.value = children
    highlightedSpouse.value = spouse
  }

  const getPersonHighlightClass = (person: Person): string => {
    const activePerson = clickedPerson.value || hoveredPerson.value
    if (!activePerson) return ''

    if (person.id === activePerson.id) return 'highlight-self'
    if (highlightedParents.value.has(person.id)) return 'highlight-parent'
    if (highlightedChildren.value.has(person.id)) return 'highlight-child'
    if (highlightedSpouse.value === person.id) return 'highlight-spouse'

    return ''
  }

  return {
    hoveredPerson,
    clickedPerson,
    highlightedParents,
    highlightedChildren,
    highlightedSpouse,
    selectPerson,
    handlePersonHover,
    handlePersonLeave,
    clearHighlights,
    updateHighlights,
    getPersonHighlightClass,
  }
}
