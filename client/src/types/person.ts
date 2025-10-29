export interface CreatePerson {
  first_name: string
  last_name: string
  sex: 'M' | 'F' | 'U'
  birth_date?: string | null
  birth_place?: string | null
  death_date?: string | null
  death_place?: string | null
  occupation?: string | null
  notes?: string | null
}
