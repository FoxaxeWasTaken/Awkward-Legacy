import { ref } from 'vue'
import type { Person } from '../types/family'
import type { Couple } from '../utils/familyUtils'

export function useTooltips() {
  const tooltip = ref({
    visible: false,
    x: 0,
    y: 0,
    person: null as Person | null,
  })

  const marriageTooltip = ref({
    visible: false,
    x: 0,
    y: 0,
    couple: null as Couple | null,
  })

  const showTooltip = (event: MouseEvent, person: Person) => {
    tooltip.value = {
      visible: true,
      x: event.pageX + 10,
      y: event.pageY - 10,
      person: person,
    }
  }

  const hideTooltip = () => {
    tooltip.value.visible = false
  }

  const showMarriageTooltip = (event: MouseEvent, couple: Couple) => {
    marriageTooltip.value = {
      visible: true,
      x: event.pageX + 10,
      y: event.pageY - 10,
      couple: couple,
    }
  }

  const hideMarriageTooltip = () => {
    marriageTooltip.value.visible = false
  }

  return {
    tooltip,
    marriageTooltip,
    showTooltip,
    hideTooltip,
    showMarriageTooltip,
    hideMarriageTooltip,
  }
}
