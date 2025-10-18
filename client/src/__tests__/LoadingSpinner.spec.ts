import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '../components/LoadingSpinner.vue'

describe('LoadingSpinner Component', () => {
  describe('Basic Rendering', () => {
    it('renders the spinner element', () => {
      const wrapper = mount(LoadingSpinner)

      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
      expect(wrapper.find('.spinner').exists()).toBe(true)
    })

    it('renders without message by default', () => {
      const wrapper = mount(LoadingSpinner)

      expect(wrapper.find('.loading-message').exists()).toBe(false)
    })

    it('renders with custom message when provided', () => {
      const message = 'Loading data...'
      const wrapper = mount(LoadingSpinner, {
        props: { message },
      })

      expect(wrapper.find('.loading-message').exists()).toBe(true)
      expect(wrapper.find('.loading-message').text()).toBe(message)
    })

    it('renders without fullscreen class by default', () => {
      const wrapper = mount(LoadingSpinner)

      expect(wrapper.find('.loading-spinner').classes()).not.toContain('fullscreen')
    })

    it('renders with fullscreen class when fullscreen prop is true', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { fullscreen: true },
      })

      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')
    })
  })

  describe('Props Validation', () => {
    it('accepts message prop as string', () => {
      const message = 'Please wait...'
      const wrapper = mount(LoadingSpinner, {
        props: { message },
      })

      expect(wrapper.props('message')).toBe(message)
    })

    it('accepts fullscreen prop as boolean', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { fullscreen: true },
      })

      expect(wrapper.props('fullscreen')).toBe(true)
    })

    it('handles undefined message prop', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { message: undefined },
      })

      expect(wrapper.find('.loading-message').exists()).toBe(false)
    })

    it('handles empty string message', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { message: '' },
      })

      expect(wrapper.find('.loading-message').exists()).toBe(false)
    })
  })

  describe('CSS Classes and Styling', () => {
    it('applies correct CSS classes to spinner element', () => {
      const wrapper = mount(LoadingSpinner)
      const spinner = wrapper.find('.spinner')

      expect(spinner.classes()).toContain('spinner')
    })

    it('applies correct CSS classes to loading message', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { message: 'Test message' },
      })
      const message = wrapper.find('.loading-message')

      expect(message.classes()).toContain('loading-message')
    })

    it('applies fullscreen class conditionally', async () => {
      const wrapper = mount(LoadingSpinner, {
        props: { fullscreen: false },
      })

      expect(wrapper.find('.loading-spinner').classes()).not.toContain('fullscreen')

      await wrapper.setProps({ fullscreen: true })
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')
    })
  })

  describe('Component Structure', () => {
    it('has correct DOM structure', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { message: 'Loading...', fullscreen: true },
      })

      const container = wrapper.find('.loading-spinner')
      expect(container.exists()).toBe(true)

      const spinner = container.find('.spinner')
      expect(spinner.exists()).toBe(true)

      const message = container.find('.loading-message')
      expect(message.exists()).toBe(true)
    })

    it('maintains proper nesting of elements', () => {
      const wrapper = mount(LoadingSpinner, {
        props: { message: 'Test' },
      })

      const container = wrapper.find('.loading-spinner')
      const spinner = container.find('.spinner')
      const message = container.find('.loading-message')

      expect(spinner.exists()).toBe(true)
      expect(message.exists()).toBe(true)
    })
  })

  describe('Accessibility', () => {
    it('renders spinner with proper structure for screen readers', () => {
      const wrapper = mount(LoadingSpinner)

      const spinner = wrapper.find('.spinner')
      expect(spinner.exists()).toBe(true)
      // The spinner should be visible and have proper styling for accessibility
    })

    it('displays loading message when provided for screen readers', () => {
      const message = 'Loading family data...'
      const wrapper = mount(LoadingSpinner, {
        props: { message },
      })

      const messageElement = wrapper.find('.loading-message')
      expect(messageElement.text()).toBe(message)
    })
  })

  describe('Edge Cases', () => {
    it('handles very long messages', () => {
      const longMessage =
        'This is a very long loading message that might wrap to multiple lines and should be handled gracefully by the component'
      const wrapper = mount(LoadingSpinner, {
        props: { message: longMessage },
      })

      expect(wrapper.find('.loading-message').text()).toBe(longMessage)
    })

    it('handles special characters in message', () => {
      const specialMessage = 'Loading... 50% ✓ ✗ ⚠️'
      const wrapper = mount(LoadingSpinner, {
        props: { message: specialMessage },
      })

      expect(wrapper.find('.loading-message').text()).toBe(specialMessage)
    })

    it('handles rapid prop changes', async () => {
      const wrapper = mount(LoadingSpinner)

      // Change fullscreen prop multiple times
      await wrapper.setProps({ fullscreen: true })
      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')

      await wrapper.setProps({ fullscreen: false })
      expect(wrapper.find('.loading-spinner').classes()).not.toContain('fullscreen')

      await wrapper.setProps({ fullscreen: true })
      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')
    })
  })

  describe('Integration', () => {
    it('works with both props simultaneously', () => {
      const wrapper = mount(LoadingSpinner, {
        props: {
          message: 'Loading family tree...',
          fullscreen: true,
        },
      })

      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')
      expect(wrapper.find('.loading-message').text()).toBe('Loading family tree...')
    })

    it('updates when props change', async () => {
      const wrapper = mount(LoadingSpinner)

      // Initially no message, no fullscreen
      expect(wrapper.find('.loading-message').exists()).toBe(false)
      expect(wrapper.find('.loading-spinner').classes()).not.toContain('fullscreen')

      // Add message
      await wrapper.setProps({ message: 'New message' })
      expect(wrapper.find('.loading-message').text()).toBe('New message')

      // Add fullscreen
      await wrapper.setProps({ fullscreen: true })
      expect(wrapper.find('.loading-spinner').classes()).toContain('fullscreen')

      // Remove message
      await wrapper.setProps({ message: undefined })
      expect(wrapper.find('.loading-message').exists()).toBe(false)

      // Remove fullscreen
      await wrapper.setProps({ fullscreen: false })
      expect(wrapper.find('.loading-spinner').classes()).not.toContain('fullscreen')
    })
  })
})
