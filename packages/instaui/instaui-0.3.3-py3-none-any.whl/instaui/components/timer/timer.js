import { ref, watch, onMounted, onUnmounted, toRef } from 'vue'


export default {
    props: ['intervalSeconds', 'active', 'once', 'immediate'],
    setup(props, { emit }) {
        const { intervalSeconds, once = false, immediate = true } = props
        const intervalId = ref(null)
        const isActive = toRef(() => props.active ?? true)
        const emitTick = once ? () => { emit('tick'); stopInterval() } : () => emit('tick')

        if (once === false) {
            watch(isActive, (value) => {
                if (value) {
                    startInterval()
                } else {
                    stopInterval()
                }
            })
        }

        const startInterval = () => {
            if (immediate) {
                emitTick()
            }

            intervalId.value = setInterval(() => {
                emitTick()
            }, intervalSeconds * 1000)
        }

        const stopInterval = () => {
            clearInterval(intervalId.value)
            emit('stop')
        }

        onMounted(() => {
            if (isActive.value) {
                startInterval()
            }
        })

        onUnmounted(() => {
            stopInterval()
        })
    }

}