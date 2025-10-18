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
    if (clickedPerson.value?.id === person.id) {
      clickedPerson.value = null
      clearHighlights()
    } else {
      clickedPerson.value = person
    }
  }

  const handlePersonHover = (person: Person) => {
    if (!clickedPerson.value) {
      hoveredPerson.value = person
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

  const findParentsInData = (data: FamilyDetailResult, person: Person, parents: Set<string>) => {
    for (const child of data.children) {
      if (child.person?.id === person.id) {
        if (data.husband?.id) parents.add(data.husband.id)
        if (data.wife?.id) parents.add(data.wife.id)
      }
    }
  }

  const findParentsInGenerations = (
    familyGenerations: FamilyGeneration[],
    person: Person,
    parents: Set<string>,
  ) => {
    for (const generation of familyGenerations) {
      for (const couple of generation.couples) {
        for (const child of couple.children) {
          if (child.id === person.id) {
            if (couple.husband?.id) parents.add(couple.husband.id)
            if (couple.wife?.id) parents.add(couple.wife.id)
          }
        }
      }
    }
  }

  const findSpouseInGenerations = (
    familyGenerations: FamilyGeneration[],
    person: Person,
  ): string | null => {
    for (const generation of familyGenerations) {
      for (const couple of generation.couples) {
        if (couple.husband?.id === person.id && couple.wife?.id) {
          return couple.wife.id
        } else if (couple.wife?.id === person.id && couple.husband?.id) {
          return couple.husband.id
        }
      }
    }
    return null
  }

  const findAllDescendants = (
    personToCheck: Person,
    crossFamilyChildren: Map<string, Person[]>,
    children: Set<string>,
  ) => {
    if (!personToCheck.has_own_family || !personToCheck.own_families) return

    for (const ownFamily of personToCheck.own_families) {
      const familyChildren = crossFamilyChildren.get(ownFamily.id) || []
      for (const child of familyChildren) {
        if (child.id && !children.has(child.id)) {
          children.add(child.id)
          findAllDescendants(child, crossFamilyChildren, children)
        }
      }
    }
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

    findParentsInData(familyData, person, parents)
    findParentsInGenerations(familyGenerations, person, parents)
    const spouse = findSpouseInGenerations(familyGenerations, person)
    findAllDescendants(person, crossFamilyChildren, children)

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
