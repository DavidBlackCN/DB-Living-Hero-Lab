export interface ImageLoadOptions { signal?: AbortSignal; timeoutMs?: number; priority?: "high" | "low" | "auto" }

export function loadImage(url: string, options: ImageLoadOptions = {}): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    let settled = false
    const timer = setTimeout(() => fail(new Error(`Image load timed out: ${url}`)), options.timeoutMs ?? 20000)
    const cleanup = () => {
      clearTimeout(timer)
      image.onload = null
      image.onerror = null
      options.signal?.removeEventListener('abort', abort)
    }
    const fail = (error: Error) => {
      if (settled) return
      settled = true
      cleanup()
      image.src = ''
      reject(error)
    }
    const abort = () => fail(new DOMException('Image load cancelled', 'AbortError'))
    options.signal?.addEventListener('abort', abort, { once: true })
    if (options.signal?.aborted) { abort(); return }
    image.crossOrigin = 'anonymous'
    image.fetchPriority = options.priority ?? 'low'
    image.onload = () => {
      if (settled) return
      settled = true
      cleanup()
      resolve(image)
    }
    image.onerror = () => fail(new Error(`Image failed to load: ${url}`))
    image.src = url
  })
}
