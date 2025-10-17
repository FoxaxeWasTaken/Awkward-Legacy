/**
 * Utility functions for date formatting and manipulation
 */

export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return dateString
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch (error) {
    console.warn('Error formatting date:', error)
    return dateString
  }
}

export const formatDateLong = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return dateString
    }
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch (error) {
    console.warn('Error formatting date:', error)
    return dateString
  }
}

export const getDateRange = (birthDate?: string, deathDate?: string): string => {
  if (!birthDate) return ''

  const formattedBirth = formatDate(birthDate)
  const formattedDeath = deathDate ? formatDate(deathDate) : 'Present'

  return `${formattedBirth} - ${formattedDeath}`
}
