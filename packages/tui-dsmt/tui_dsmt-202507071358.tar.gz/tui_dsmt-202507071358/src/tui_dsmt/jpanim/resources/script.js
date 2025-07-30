const {createApp, ref, reactive, onMounted, onUnmounted} = Vue

const app = createApp({
    setup() {
        let current = ref(1)
        let frame = reactive({})

        function set(c) {
            current.value = Math.max(1, Math.min(c, app.frames.length))

            Object.keys(frame).forEach(key => delete frame[key])
            for (let i = 0; i < current.value; i++) {
                Object.assign(frame, app.frames[i])
            }
        }

        set(1);

        // <injected js>

        return {
            current: current,
            count: app.frames.length,
            previous: (o = 1) => set(current.value - o),
            next: (o = 1) => set(current.value + o),
            frame: frame,
        }
    }
})
