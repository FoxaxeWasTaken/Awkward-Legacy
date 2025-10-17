import type { FamilyDetailResult, Person, Event } from '../types/family'

export interface Couple {
  id: string
  husband?: Person
  wife?: Person
  children: Person[]
  marriageDate?: string
  marriagePlace?: string
  events: Event[]
  isMarried: boolean
  isDivorced: boolean
  divorceDate?: string
  divorcePlace?: string
}

export interface FamilyGeneration {
  couples: Couple[]
}

/**
 * Analyze relationship events to determine marriage and divorce status
 */
export const analyzeRelationshipEvents = (events: Event[], marriageDate?: string) => {
  const marriageEvents = events.filter(
    (event) =>
      event.type?.toLowerCase().includes('marriage') ||
      event.type?.toLowerCase().includes('wedding') ||
      event.type?.toLowerCase().includes('marry'),
  )

  const divorceEvents = events.filter(
    (event) =>
      event.type?.toLowerCase().includes('divorce') ||
      event.type?.toLowerCase().includes('separation') ||
      event.type?.toLowerCase().includes('annulment'),
  )

  // Consider a couple married if they have marriage events OR a marriage date
  const isMarried = marriageEvents.length > 0 || !!marriageDate
  const isDivorced = divorceEvents.length > 0

  // Get the most recent divorce event
  const sortedDivorceEvents = [...divorceEvents].sort((a: Event, b: Event) => {
    if (!a.date || !b.date) return 0
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })
  const latestDivorce = sortedDivorceEvents[0]

  return {
    isMarried,
    isDivorced,
    divorceDate: latestDivorce?.date,
    divorcePlace: latestDivorce?.place,
    marriageEvents,
    divorceEvents,
  }
}

/**
 * Create family generations from family data
 */
export const createFamilyGenerations = (
  familyData: FamilyDetailResult,
  crossFamilyChildren: Map<string, Person[]>,
): FamilyGeneration[] => {
  const generations: FamilyGeneration[] = []

  // Analyze relationship events for the main couple
  const relationshipAnalysis = analyzeRelationshipEvents(
    familyData.events,
    familyData.marriage_date,
  )

  // Create the main couple (current family)
  const mainCouple: Couple = {
    id: familyData.id,
    husband: familyData.husband || undefined,
    wife: familyData.wife || undefined,
    children: familyData.children.map((child) => child.person).filter(Boolean) as Person[],
    marriageDate: familyData.marriage_date,
    marriagePlace: familyData.marriage_place,
    events: familyData.events,
    isMarried: relationshipAnalysis.isMarried,
    isDivorced: relationshipAnalysis.isDivorced,
    divorceDate: relationshipAnalysis.divorceDate,
    divorcePlace: relationshipAnalysis.divorcePlace,
  }

  // Add main couple to first generation
  generations.push({
    couples: [mainCouple],
  })

  // Recursively process all generations
  let currentGenCouples = [mainCouple]

  while (currentGenCouples.length > 0) {
    const nextGenCouples: Couple[] = []

    // For each couple in the current generation, find their children who have families
    for (const couple of currentGenCouples) {
      const coupleChildren = couple.children

      for (const child of coupleChildren) {
        if (child.has_own_family && child.own_families) {
          for (const ownFamily of child.own_families) {
            const childFamilyData = crossFamilyChildren.get(ownFamily.id)

            if (ownFamily.spouse || childFamilyData) {
              // For child couples, we need to fetch their events
              // Analyze relationship events for the child couple
              const childRelationshipAnalysis = analyzeRelationshipEvents(
                ownFamily.events || [],
                ownFamily.marriage_date,
              )

              const childCouple: Couple = {
                id: ownFamily.id,
                husband: child.sex === 'M' ? child : undefined,
                wife: child.sex === 'F' ? child : undefined,
                children: childFamilyData || [],
                marriageDate: ownFamily.marriage_date,
                marriagePlace: ownFamily.marriage_place,
                events: ownFamily.events || [],
                isMarried: childRelationshipAnalysis.isMarried,
                isDivorced: childRelationshipAnalysis.isDivorced,
                divorceDate: childRelationshipAnalysis.divorceDate,
                divorcePlace: childRelationshipAnalysis.divorcePlace,
              }

              // Add spouse
              if (ownFamily.spouse) {
                if (child.sex === 'M') {
                  childCouple.wife = {
                    id: ownFamily.spouse.id,
                    first_name: ownFamily.spouse.name.split(' ')[0],
                    last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
                    sex: ownFamily.spouse.sex,
                    has_own_family: false,
                  }
                } else {
                  childCouple.husband = {
                    id: ownFamily.spouse.id,
                    first_name: ownFamily.spouse.name.split(' ')[0],
                    last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
                    sex: ownFamily.spouse.sex,
                    has_own_family: false,
                  }
                }
              }

              nextGenCouples.push(childCouple)
            }
          }
        }
      }
    }

    // Add next generation if it exists
    if (nextGenCouples.length > 0) {
      generations.push({
        couples: nextGenCouples,
      })
      currentGenCouples = nextGenCouples
    } else {
      break
    }
  }

  return generations
}

/**
 * Get gender icon for a person
 */
export const getGenderIcon = (sex: 'M' | 'F' | 'U'): string => {
  switch (sex) {
    case 'M':
      return '👨'
    case 'F':
      return '👩'
    default:
      return '👤'
  }
}

/**
 * Get child gender icon
 */
export const getChildGenderIcon = (sex: 'M' | 'F' | 'U'): string => {
  switch (sex) {
    case 'M':
      return '👦'
    case 'F':
      return '👧'
    default:
      return '👤'
  }
}
