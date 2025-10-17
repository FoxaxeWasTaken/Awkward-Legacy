/**
 * Utility functions for date formatting and manipulation
 */

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch (_error) {
    return dateString
  }
}

export const formatDateLong = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch (_error) {
    return dateString
  }
}

export const getDateRange = (birthDate?: string, deathDate?: string): string => {
  if (!birthDate) return ''

  const formattedBirth = formatDate(birthDate)
  const formattedDeath = deathDate ? formatDate(deathDate) : 'Present'

  return `${formattedBirth} - ${formattedDeath}`
}
