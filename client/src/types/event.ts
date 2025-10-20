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

// Types d'événements familiaux
export const FAMILY_EVENT_TYPES = [
  { value: 'Marriage', label: 'Mariage' },
  { value: 'Couple', label: 'Couple' },
  { value: 'Engagement', label: 'Fiançailles' },
  { value: 'Divorce', label: 'Divorce' },
  { value: 'Separation', label: 'Séparation' },
  { value: 'Cohabitation', label: 'Ménage commun' },
  { value: 'Marriage Annulment', label: 'Annulation mariage' },
] as const

