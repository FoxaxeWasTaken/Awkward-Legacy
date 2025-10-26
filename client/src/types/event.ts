export interface Event {
  id: string
  person_id?: string | null
  family_id?: string | null
  type: string
  date?: string | null
  place?: string | null
  description?: string | null
}

export interface CreateEvent {
  person_id?: string | null
  family_id?: string | null
  type: string
  date?: string | null
  place?: string | null
  description?: string | null
}

// Family event types
export const FAMILY_EVENT_TYPES = [
  { value: 'Marriage', label: 'Marriage' },
  { value: 'Couple', label: 'Couple' },
  { value: 'Engagement', label: 'Engagement' },
  { value: 'Divorce', label: 'Divorce' },
  { value: 'Separation', label: 'Separation' },
  { value: 'Cohabitation', label: 'Cohabitation' },
  { value: 'Marriage Annulment', label: 'Marriage Annulment' },
] as const




