export interface Person {
  id: string
  first_name: string
  last_name: string
  sex: 'M' | 'F' | 'U'
  birth_date?: string
  death_date?: string
  birth_place?: string
  death_place?: string
  occupation?: string
  notes?: string
  has_own_family?: boolean
  own_families?: OwnFamily[]
}

export interface OwnFamily {
  id: string
  marriage_date?: string
  marriage_place?: string
  spouse?: {
    id: string
    name: string
    sex: 'M' | 'F'
  }
}

export interface Child {
  id: string
  family_id: string
  person_id: string
  person?: Person
}

export interface Event {
  id: string
  family_id: string
  event_type: string
  date?: string
  place?: string
  notes?: string
}

export interface FamilySearchResult {
  id: string
  husband_name?: string
  wife_name?: string
  marriage_date?: string
  marriage_place?: string
  children_count: number
  summary: string
}

export interface FamilyDetailResult {
  id: string
  husband_id?: string
  wife_id?: string
  marriage_date?: string
  marriage_place?: string
  notes?: string
  husband?: Person
  wife?: Person
  children: Child[]
  events: Event[]
}

export interface FamilySearchParams {
  q?: string
  family_id?: string
  limit?: number
}
