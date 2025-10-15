export interface CreatePerson {
  first_name: string
  last_name: string
  sex: 'M' | 'F' | 'U'
  birth_date: string,
  birth_place: string,
  death_date: string,
  death_place: string,
  notes: string
}
