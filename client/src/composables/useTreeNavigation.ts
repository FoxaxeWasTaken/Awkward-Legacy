import { ref, nextTick } from 'vue'

export function useTreeNavigation() {
  const panX = ref(0)
  const panY = ref(0)
  const scale = ref(1)
  const isDragging = ref(false)
  const dragStart = ref({ x: 0, y: 0 })
  const panStart = ref({ x: 0, y: 0 })

  const startDrag = (e: MouseEvent) => {
    // Allow drag from anywhere
    isDragging.value = true
    dragStart.value = { x: e.clientX, y: e.clientY }
    panStart.value = { x: panX.value, y: panY.value }
  }

  const handleDrag = (e: MouseEvent) => {
    if (!isDragging.value) return

    const dx = e.clientX - dragStart.value.x
    const dy = e.clientY - dragStart.value.y

    // Only start panning if moved more than 3 pixels (to allow clicks)
    const distance = Math.sqrt(dx * dx + dy * dy)
    if (distance > 3) {
      panX.value = panStart.value.x + dx
      panY.value = panStart.value.y + dy
    }
  }

  const stopDrag = () => {
    isDragging.value = false
  }

  const handleWheel = (e: WheelEvent, treeContainer: HTMLElement | undefined) => {
    e.preventDefault()

    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newScale = Math.min(Math.max(0.1, scale.value * delta), 3)

    // Zoom towards mouse position
    if (treeContainer) {
      const rect = treeContainer.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      // Calculate the point in the content that's under the mouse
      const contentX = (mouseX - panX.value) / scale.value
      const contentY = (mouseY - panY.value) / scale.value

      // Update pan to keep that point under the mouse after zoom
      panX.value = mouseX - contentX * newScale
      panY.value = mouseY - contentY * newScale
    }

    scale.value = newScale
  }

  const zoomIn = (treeContainer: HTMLElement | undefined) => {
    const newScale = Math.min(scale.value * 1.1, 3)

    // Zoom towards center
    if (treeContainer) {
      const rect = treeContainer.getBoundingClientRect()
      const centerX = rect.width / 2
      const centerY = rect.height / 2

      const contentX = (centerX - panX.value) / scale.value
      const contentY = (centerY - panY.value) / scale.value

      panX.value = centerX - contentX * newScale
      panY.value = centerY - contentY * newScale
    }

    scale.value = newScale
  }

  const zoomOut = (treeContainer: HTMLElement | undefined) => {
    const newScale = Math.max(scale.value / 1.1, 0.1)

    // Zoom towards center
    if (treeContainer) {
      const rect = treeContainer.getBoundingClientRect()
      const centerX = rect.width / 2
      const centerY = rect.height / 2

      const contentX = (centerX - panX.value) / scale.value
      const contentY = (centerY - panY.value) / scale.value

      panX.value = centerX - contentX * newScale
      panY.value = centerY - contentY * newScale
    }

    scale.value = newScale
  }

  const resetZoom = () => {
    scale.value = 1
    panX.value = 0
    panY.value = 0
  }

  const fitTreeToView = async (
    treeContainer: HTMLElement | undefined,
    treeContent: HTMLElement | undefined,
  ) => {
    // Wait for next tick to ensure DOM is updated
    await nextTick()

    if (!treeContainer || !treeContent) return

    const containerRect = treeContainer.getBoundingClientRect()
    const contentRect = treeContent.getBoundingClientRect()

    // Calculate scale to fit content with some padding (90% of container)
    const scaleX = (containerRect.width * 0.9) / contentRect.width
    const scaleY = (containerRect.height * 0.9) / contentRect.height
    const newScale = Math.min(scaleX, scaleY, 1) // Don't zoom in beyond 100%

    // Calculate pan to center the content
    const scaledWidth = contentRect.width * newScale
    const scaledHeight = contentRect.height * newScale

    panX.value = (containerRect.width - scaledWidth) / 2
    panY.value = (containerRect.height - scaledHeight) / 2 + 50 // Add offset for header
    scale.value = newScale
  }

  return {
    panX,
    panY,
    scale,
    isDragging,
    dragStart,
    panStart,
    startDrag,
    handleDrag,
    stopDrag,
    handleWheel,
    zoomIn,
    zoomOut,
    resetZoom,
    fitTreeToView,
  }
}
